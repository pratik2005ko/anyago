import socket

SOCKET_PATH = "/tmp/anya.sock"

try:
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect(SOCKET_PATH)
    client.sendall(b"CLOSE")
    client.close()
except Exception as e:
    print(f"Anya close daemon nahi chal raha: {e}")