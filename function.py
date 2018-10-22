import socket
import json
import logging
import struct
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


logging.basicConfig(level=logging.DEBUG)

base_max_count = 70
download_url = {
    "server_feralhosting":u"http://cloud.etenal.me/download/"
}
base_path = {
    "server_feralhosting":u'/media/f3db/etenalcxz/www/cloud.etenal.me/public_html/download/'
}

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

class Interface():
    def __init__(self):
        self.connection = None
        self.socket_instance = None
        self.pwd = None
        self.subpath = ""
        self.max_count = base_max_count

    def is_alive(self, signature):
        try:
            send_msg(self.socket_instance, 'Greeting')
        except:
            return False
        data = recv_msg(self.socket_instance)
        if data != signature:
            self.close_socket()
            logging.debug("[is alive] signature miss : " + data)
            return False
        return True

    def start_socket(self, HOST, signature):
        PORT = 3777  # The same port as used by the server
        self.socket_instance = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_instance.connect((HOST, PORT))
        self.connection = signature
        self.pwd = base_path[signature]
        self.url_length = 94
        return True


    def close_socket(self):
        self.socket_instance.close()

    """
    {
    command:
    server:
    date:
    receive:[{name:,create_date:,size:,type:[file/dir]}]
    }
    """
    def parse_data(self, data):
        logging.debug(data)
        r = json.loads(data)
        return r


    def connection_check(self, HOST, signature):
        if self.connection != None:
            if signature != self.connection:
                self.close_socket()
                self.start_socket(HOST, signature)
            if not self.is_alive(signature):
                self.start_socket(HOST, signature)
        else:
            self.start_socket(HOST, signature)

    def fc_list(self, HOST, signature, offset):
        logging.debug("[list enter] host:" + HOST)
        self.connection_check(HOST, signature)
        command = u'ls ' + self.pwd + self.subpath
        logging.debug("[list sending message] "+command)
        send_msg(self.socket_instance, command.encode('utf-8'))
        data = recv_msg(self.socket_instance)
        if data==None:
            self.close_socket()
        logging.debug("[list outcoming message] "+data)
        r = self.parse_data(data)
        markup = InlineKeyboardMarkup()
        button_list = []
        markup.row_width = 2
        logging.debug('[list] numbers of button:'+str(len(r['receive'])))


        all_files = sorted(r['receive'],key= lambda i: i['name'])
        count = 1
        self.url_length = 94
        logging.debug("[new max count] "+str(self.max_count))
        for file in all_files[offset:]:
            count += 1
            if file['type']=='file':
                self.url_length +=
                button_list.append(
                    InlineKeyboardButton(file['name'],url=download_url[signature]+self.subpath+file['name'])
                )
            else:
                button_list.append(
                    InlineKeyboardButton(file['name'], switch_inline_query_current_chat='cd '+file['name'])
                )
            if count >= self.max_count:
                button_list.append(
                    InlineKeyboardButton("More", switch_inline_query_current_chat='ls +'+str(offset+self.max_count))
                )
                break
        markup.add(*button_list)
        return markup


    def fc_cd(self,HOST, signature, _dir):
        self.connection_check(HOST, signature)
        if _dir == u"..":
            try:
                p = self.subpath.rfind(u"/", 0, len(self.subpath) - 1)
                if p == -1:
                    p=0
                a = self.subpath[:p]
            except:
                a = ""
            self.subpath = a
        else:
            self.subpath += _dir
        if not self.pwd.endswith(u"/"):
            self.subpath += u"/"

