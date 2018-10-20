import socket
import json
import struct

HOST = 'hypnos.feralhosting.com'
PORT = 3777
signature = 'server_feralhosting'
base_path = '/media/f3db/etenalcxz/www/cloud.etenal.me/public_html/download/'

def send(sk, text):
    msg = struct.pack('>I', len(text)) + text
    sk.sendall(msg)

def recv_msg(sock):
    # Read message length and unpack it into an integer
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    return recvall(sock, msglen)

def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def test_socket():
    PORT = 3777  # The same port as used by the server
    socket_instance = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_instance.connect((HOST, PORT))
    send(socket_instance, 'Greeting')
    data = recv_msg(socket_instance)
    assert (data==signature)
    socket_instance.close()

def test_ls():
    PORT = 3777
    data = ''
    socket_instance = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_instance.connect((HOST, PORT))
    send(socket_instance, 'Greeting')
    data = recv_msg(socket_instance)
    assert (data == signature)
    send(socket_instance,'ls '+base_path)
    data = recv_msg(socket_instance)
    r = json.loads(data)


if __name__ == "__main__":
    test_socket()
    test_ls()
