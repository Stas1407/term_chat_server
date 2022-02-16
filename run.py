from misc.Room import Room
import asyncio
from Server import Server


async def main(host, port):
    room = Room("main", True)
    rooms_dict = {"main": room}
    loop = asyncio.get_running_loop()
    print("[+] Starting server")
    server = await loop.create_server(lambda: Server(rooms_dict), host, port)
    print("[+] Listening")
    await server.serve_forever()

try:
    asyncio.run(main('127.0.0.1', 5000))
except KeyboardInterrupt:
    print("[+] Exiting")