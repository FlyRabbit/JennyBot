import telebot
from telebot import types
import logging
from function import Interface


logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

API_TOKEN = "API_TOKEN"
bot = telebot.TeleBot(API_TOKEN)
server = "hypnos.feralhosting.com"
signature = "server_feralhosting"
interface = Interface()
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
        types.InlineKeyboardButton("FeralHosting", callback_data="server_feralhosting"))
    return markup


def command_markup():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        types.InlineKeyboardButton("list", callback_data="command_list", switch_inline_query_current_chat="list "))
    return markup

def files_markup(markup):
    return markup

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global server
    if call.data == "server_feralhosting":
        bot.answer_callback_query(call.id, "Connecting to feralhosting")
        signature = call.data
        server = host_list[signature]

    if call.data == "command_list":
        pass

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


@bot.message_handler(func=lambda message: True)
def echo_message(message):
    if message.text[:18] == "@etenalJennyBot ls":
        message.text = message.text[18:]
        list_files(message)

    if message.text[:18] == "@etenalJennyBot cd":
        message.text = message.text[18:]
        cd_directory(message)


bot.remove_webhook()
bot.polling(none_stop=True)