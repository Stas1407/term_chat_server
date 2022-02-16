from cryptography.fernet import Fernet
from pyDH import DiffieHellman
import base64


class Session:
    def __init__(self, transport):
        self._transport = transport
        self._dh = DiffieHellman()
        self._fernet = ""

    def _send(self, data):
        self._transport.write(json.dumps(data).encode("utf-8"))

    def send(self, data):
        data = json.dumps(data).encode("utf-8")
        data = self._fernet.encrypt(data)
        self._transport.write(data)

    def decrypt(self, data):
        data = self._fernet.decrypt(data)
        data = json.loads(data)
        return data

    def handle_test_message(self, msg):
        msg = self.decrypt(msg)
        username = msg["username"]
        self.send(msg)

        return username

    def create_session(self, client_pub_key):
        # Calculate shared key
        shared_key = self._dh.gen_shared_key(client_pub_key)
        shared_key = base64.b64encode(bytes.fromhex(shared_key))
        self._fernet = Fernet(shared_key)

    def close(self):
        self._transport.close()

    def start(self):
        # Send public key to the client
        public_key = self._dh.gen_public_key()
        self._send({"public_key": public_key})
