import asyncio
import json
from misc.Room import Room
from misc.Session import Session

TIMEOUT = 120


class Server(asyncio.Protocol):
    def __init__(self, rooms):
        # Timeout handling
        loop = asyncio.get_running_loop()
        self._timeout_handle = loop.call_later(TIMEOUT, self._quit)

        # Info
        self._ip = ""
        self._port = ""
        self._room = ""
        self._rooms_dict = rooms
        self._mode = "command"
        self._username = ""

        # Session
        self._session = Session("")
        self._stage = 1

    def _list_rooms(self):
        t = [["Room name", "People"]]
        for name, room in self._rooms_dict.items():
            if room.is_public:
                t.append([name, room.number_of_members()])

        return t

    def _schedule_new_timeout(self):
        self._timeout_handle.cancel()
        loop = asyncio.get_running_loop()
        self._timeout_handle = loop.call_later(TIMEOUT, self._quit)

    def message_from_room(self, data):
        self._session.send(data)
    
    def _handle_session_creating(self, data):
        if self._stage == 1:
            try:
                data = json.loads(data.decode("utf-8"))
                client_pub_key = data["public_key"]
                self._session.create_session(client_pub_key)
                self._stage += 1
            except KeyError:
                print("[-] misc didn't send public key")
                self._quit(False)
        elif self._stage == 2:
            try:
                self._username = self._session.handle_test_message(data)
                self._stage += 1
            except Exception:
                print("[-] Error while handling test message")
                self._quit(False)

    def _join_room(self, data):
        self._room = data["args"]["room_name"]

        if self._room in self._rooms_dict:
            self._rooms_dict[self._room].join(self)
            self._mode = "text"
            self._session.send({"state": "success"})
        else:
            self._room = ""
            self._session.send({"state": "failed"})

    def _create_room(self, data):
        name, is_public = data["args"]["name"], data["args"]["is_public"]

        if name in self._rooms_dict:
            self._session.send({"state": "failed"})
            return

        room = Room(name, is_public)
        self._rooms_dict[name] = room
        self._session.send({"state": "success"})

    def _quit_chat_mode(self):
        self._mode = "command"
        self._rooms_dict[self._room].leave(self)
        self._room = ""
        self._session.send({"message": "quit"})

    def _send_to_members_of_the_room(self, data):
        data["sender"] = self._username
        for participant in self._rooms_dict[self._room].members:
            if participant != self:
                participant.message_from_room(data)

    def connection_made(self, transport):
        ip, port = transport.get_extra_info("peername")
        print(f"[+] Got a connection - {ip}:{port}")

        self._ip = ip
        self._port = port
        self._session = Session(transport)
        self._session.start()

    def data_received(self, data):
        self._schedule_new_timeout()
        
        if self._stage < 3:
            self._handle_session_creating(data)
            return

        data = self._session.decrypt(data)

        try:
            if self._mode == "command":
                if data["command"] == "list":
                    self._session.send(self._list_rooms())
                elif data["command"] == "join":
                    self._join_room(data)
                elif data["command"] == "quit":
                    self._quit(timeout=False)
                elif data["command"] == "new":
                    self._create_room(data)
            elif self._mode == "text":
                if data["message"] == "quit":
                    self._quit_chat_mode()
                else:
                    self._send_to_members_of_the_room(data)
        except KeyError as e:
            print("[-] Wrong query from the client")

    def _quit(self, timeout=True):
        if timeout:
            print(f"[-] Timeout. Shutting down {self._ip}:{self._port}")
        else:
            print(f"[*] Closing connection - {self._ip}:{self._port}")

        if self._room != "":
            self._rooms_dict[self._room].leave(self)
        self._session.close()

