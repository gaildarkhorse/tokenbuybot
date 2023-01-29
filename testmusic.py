import requests
import telebot
import urllib3
import time

urllib3.disable_warnings()
bot = telebot.TeleBot("5751416719:AAE3qCgK6zeKs9YL0sKe9y1UOyedpcxm4tk")




@bot.message_handler(commands = ['start'])
def starting(message):
    bot.send_message(message.chat.id, "ok")

@bot.message_handler(content_types = ['text'])
def name(message):
    r = requests.Session()

    headers = {
        'user-agent':
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"}

    params = {'search': message.text, 'time': time.ctime()}
    msg = bot.send_audio(chat_id = message.chat.id, audio = "https://vk.music7s.cc/get.php?id=-190572601_456239079")
    print(msg.audio.file_id)


bot.polling(none_stop = True)