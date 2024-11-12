import telebot
from config import botkey
from datetime import datetime
import pytz
from telebot import types

bot = telebot.TeleBot(botkey)

# Функция для создания клавиатуры
def create_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)  # Создание клавиатуры
    button_help = types.KeyboardButton('Help')  # Кнопка "Help"
    button_time = types.KeyboardButton('Time')  # Кнопка "Time"
    markup.add(button_help, button_time)  # Добавляем кнопки на клавиатуру
    return markup

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_name = message.from_user.first_name  # Получаем имя пользователя
    # Отправляем сообщение с клавиатурой
    bot.send_message(message.chat.id, f'Привет, {user_name}❗️', reply_markup=create_keyboard())

@bot.message_handler(content_types=['text'])
def handle_text(message):
    # Обрабатываем нажатие на кнопки
    if message.text == 'Help':
        bot.send_message(message.chat.id, '😀 Я - тестовый бот❗️', reply_markup=create_keyboard())
    elif message.text == 'Time':
        # Устанавливаем часовой пояс Москвы
        moscow_tz = pytz.timezone('Europe/Moscow')
        # Получаем текущее время в Москве
        moscow_time = datetime.now(moscow_tz).strftime('%H:%M:%S')
        bot.send_message(message.chat.id, f'Текущее время в Москве: {moscow_time}', reply_markup=create_keyboard())

@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, '😀 Я - тестовый бот❗️', reply_markup=create_keyboard())

bot.polling()
