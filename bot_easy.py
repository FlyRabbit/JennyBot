import telebot
from telebot import types
import logging
from function import Interface


logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

API_TOKEN = "638630435:AAHf0P4SXPG5JS_6k9e4cgjN9fLdqPvuVvY"
bot = telebot.TeleBot(API_TOKEN)
server = None
signature = None
interface = Interface()
signature_list = {
    "FeralHosting":"server_feralhosting"
}
host_list = {
    "server_feralhosting":"hypnos.feralhosting.com"
}

def _list(message):
    b = message.text.split("+")
    if len(b)>1:
        offset = int(b[1])
    else:
        offset = 0
    markup = interface.fc_list(server, signature, offset)
    bot.send_message(message.chat.id, "Download", reply_markup=files_markup(markup))


def _cd(message):
    b = message.text.split(" ")
    if len(b)>1:
        _dir = b[1]
        if len(b)>2:
            for i in range(2,len(b)):
                _dir += " " + b[i]
    else:
        _dir = ""
    interface.fc_cd(server, signature, _dir)
    markup = interface.fc_list(server, signature, 0)
    bot.send_message(message.chat.id, _dir, reply_markup=files_markup(markup))


def check_master(user_id):
    if user_id==436924050:
        return True
    else:
        bot.send_message(user_id, "You are not my master.")
        return False


def server_markup():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        types.InlineKeyboardButton("FeralHosting", switch_inline_query_current_chat="server FeralHosting"))
    return markup



def command_markup():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        types.InlineKeyboardButton("list", callback_data="command_list", switch_inline_query_current_chat="list "))
    return markup

def files_markup(markup):
    return markup

"""
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global server
    global signature
    if call.data == "server_feralhosting":
        bot.answer_callback_query(call.id, "Connecting to feralhosting")
        signature = call.data
        server = host_list[signature]

    if call.data == "command_list":
        pass
"""

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if check_master(message.chat.id):
        bot.send_message(message.chat.id, "Hello ETenal",reply_markup=command_markup())

@bot.message_handler(commands=['list','ls'])
def list_files(message):
    logging.debug("[lsit incoming message] "+ message.text)
    if check_master(message.chat.id):
        if server==None:
            bot.send_message(message.chat.id, "Choose a server",reply_markup=server_markup())
        else:
            _list(message)

@bot.message_handler(commands=['cd'])
def cd_directory(message):
    if check_master(message.chat.id):
        if server==None:
            bot.send_message(message.chat.id, "Choose a server",reply_markup=server_markup())
        else:
            _cd(message)

@bot.message_handler(commands=['server'])
def choose_server(message):
    global server
    global signature
    if check_master(message.chat.id):
        s = message.text.split(" ")
        if len(s)==1:
            bot.send_message(message.chat.id, "Choose a server", reply_markup=server_markup())
        else:
            try:
                signature = signature_list[s[1]]
                server = host_list[signature]
                bot.reply_to(message, "Set server successfully.")
            except:
                bot.reply_to(message, "Set server failed.")


@bot.message_handler(func=lambda message: True)
def parse_command(message):
    if message.text[:18] == "@etenalJennyBot ls":
        message.text = message.text[16:]
        logging.debug("[parse command] "+message.text)
        list_files(message)

    if message.text[:18] == "@etenalJennyBot cd":
        message.text = message.text[16:]
        logging.debug("[parse command] " + message.text)
        cd_directory(message)

    if message.text[:22] == "@etenalJennyBot server":
        message.text = message.text[16:]
        logging.debug("[parse command] " + message.text)
        choose_server(message)


bot.remove_webhook()
bot.polling(none_stop=True)