# term_chat_server

Server for https://github.com/Stas1407/term_chat \
Uses asyncio to handle multiple clients and encryption (Diffie Hellman (pyDH) + cryptography.fernet) to ensure secure connection.

## Usage:
1. `pip install -r requirements.txt`
2. Change ip and port in run.py (optional)
3. `python3 run.py`
