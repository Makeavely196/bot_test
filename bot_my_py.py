import telebot
from config import botkey
from datetime import datetime
import pytz

bot = telebot.TeleBot(botkey)

@bot.message_handler(commands=['start'])
def handle_message(message):
    user_name = message.from_user.first_name  # Получаем имя пользователя
    bot.send_message(message.chat.id, f'Привет, {user_name}❗️')  # Приветствие с именем пользователя

@bot.message_handler(commands=['help'])
def handle_message(message):
    bot.send_message(message.chat.id, '😀 Я - тестовый бот❗️')

@bot.message_handler(commands=['time'])
def send_time(message):
    # Устанавливаем часовой пояс Москвы
    moscow_tz = pytz.timezone('Europe/Moscow')
    # Получаем текущее время в Москве
    moscow_time = datetime.now(moscow_tz).strftime('%H:%M:%S')
    bot.send_message(message.chat.id, f'Текущее время в Москве: {moscow_time}')

bot.polling()
