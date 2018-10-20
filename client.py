import socket
import logging
import scandir
import datetime
import json
import struct

HOST = ''
PORT = 3777
SERVER = 'server_feralhosting'

logging.basicConfig(level=logging.DEBUG)

def send_msg(sock, msg):
    # Prefix each message with a 4-byte length (network byte order)
    msg = struct.pack('>I', len(msg)) + msg
    sock.sendall(msg)

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

def scan(path):
    result = []
    logging.debug('[scan] Start scan '+path)
    files = scandir.scandir(path)
    for each in files:
        if each.is_dir(follow_symlinks=False):
            result.append(
                {'name': each.name, 'create_data': 0, 'size': 0, 'type': 'dir'}
            )
        else:
            result.append(
                {'name': each.name, 'create_data': 0, 'size': 0, 'type': 'file'}
            )
    return result


def start_socket():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(1)
    conn, addr = s.accept()
    logging.debug('New connection')
    while 1:
        data = recv_msg(conn)
        #data = conn.recv(1024)
        if not data:
            logging.debug("Close connection")
            s.close()
            break
        r = parse_incoming_message(data)
        try:
            logging.debug('[sending message] ' + r)
            #conn.sendall(r)
            send_msg(conn,r)
        except :
            s.close()
            break

def parse_incoming_message(data):
    logging.debug('[incoming message] ' + data)
    command = data.split(' ')
    res = {}

    if command[0]=='Greeting':
        return SERVER

    if command[0]=='list' or command[0]=='ls':
        res['command'] = 'list'
        res['server'] = SERVER
        res['date'] = str(datetime.datetime.now())
        path = command[1]
        if len(command)>2:
            for i in range(2,len(command)):
                path += " " + command[i]
        res['receive'] = scan(path)

    raw_data = json.dumps(res)
    return raw_data


if __name__ == "__main__":
    while 1:
        start_socket()
