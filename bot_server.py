import telebot
from flask import Flask, request, abort
import logging
import time

WEBHOOK_LISTEN = '0.0.0.0'
API_TOKEN = "638630435:AAHf0P4SXPG5JS_6k9e4cgjN9fLdqPvuVvY"
WEBHOOK_URL_BASE = "https://bot.etenal.me/"

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

botServer = Flask(__name__)

bot = telebot.AsyncTeleBot(API_TOKEN)
req = bot.get_webhook_info()
logging.info("[logging]"+req.url)


@botServer.route("/"+API_TOKEN, methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

@botServer.route("/")
def hello():
    bot.remove_webhook()
    time.sleep(0.1)
    bot.set_webhook(url=WEBHOOK_URL_BASE + API_TOKEN)
    return "Hello Jenny!", 200

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(436924050, "Here is jenny")

@bot.message_handler(commands=['echo'])
def echo(message):
    bot.send_message(436924050, "Greet")

# Handle all other messages
@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_message(message):
    bot.reply_to(message, message.text)

if __name__ == "__main__":
    botServer.run(
        host=WEBHOOK_LISTEN,
        debug=True)