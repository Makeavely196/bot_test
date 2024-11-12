import telebot
import random
from telebot import types
from config import botkey

bot = telebot.TeleBot(botkey)

# Карты и ранги для игры в покер
suits = ['♠️', '♥️', '♣️', '♦️']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
deck = [f"{rank}{suit}" for suit in suits for rank in ranks]

# Состояние игры
players = {}
game_in_progress = False

# Функция для создания клавиатуры
def create_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_play = types.KeyboardButton('Играть в покер')  # Кнопка для начала игры
    button_end = types.KeyboardButton('Завершить игру')   # Кнопка для завершения игры
    markup.add(button_play, button_end)
    return markup

@bot.message_handler(commands=['start'])
def handle_start(message):
    # Отправляем приветственное сообщение и клавиатуру
    bot.send_message(message.chat.id, "Добро пожаловать! Нажмите 'Играть в покер', чтобы начать игру или 'Завершить игру', чтобы выйти.", reply_markup=create_keyboard())

@bot.message_handler(func=lambda message: message.text == 'Играть в покер')
def start_game(message):
    global game_in_progress, players, deck
    if game_in_progress:
        bot.send_message(message.chat.id, "Игра уже идет! Чтобы начать новую игру, сначала завершите текущую.")
    else:
        game_in_progress = True
        players = {}  # Сбросим список игроков
        deck = [f"{rank}{suit}" for suit in suits for rank in ranks]  # Перемешиваем колоду
        random.shuffle(deck)
        bot.send_message(message.chat.id, "Игра началась! Введите /join чтобы присоединиться.")
        bot.send_message(message.chat.id, "Когда все игроки присоединятся, нажмите 'Играть в покер' для раздачи карт.")

@bot.message_handler(commands=['join'])
def join_game(message):
    if not game_in_progress:
        bot.send_message(message.chat.id, "Сначала начните игру, нажав 'Играть в покер'.")
        return
    if message.from_user.id in players:
        bot.send_message(message.chat.id, "Вы уже присоединились!")
    else:
        players[message.from_user.id] = {"name": message.from_user.first_name, "hand": []}
        bot.send_message(message.chat.id, f"{message.from_user.first_name} присоединился к игре!")

@bot.message_handler(func=lambda message: message.text == 'Завершить игру')
def end_game(message):
    global game_in_progress, players
    if not game_in_progress:
        bot.send_message(message.chat.id, "Игра не начата. Нажмите 'Играть в покер' для начала новой игры.")
    else:
        game_in_progress = False
        players = {}
        bot.send_message(message.chat.id, "Игра завершена! Нажмите 'Играть в покер' для новой игры.", reply_markup=create_keyboard())

@bot.message_handler(func=lambda message: message.text == 'Играть в покер' and game_in_progress)
def deal_cards(message):
    if not game_in_progress:
        bot.send_message(message.chat.id, "Сначала начните игру, нажав 'Играть в покер'.")
        return
    if len(players) < 2:
        bot.send_message(message.chat.id, "Для игры необходимо минимум два игрока!")
        return
    # Раздаем каждому игроку по две карты
    for player_id, player_info in players.items():
        player_info["hand"] = [deck.pop(), deck.pop()]
        hand = ", ".join(player_info["hand"])
        bot.send_message(player_id, f"Ваши карты: {hand}")
    bot.send_message(message.chat.id, "Карты разданы! Для завершения игры нажмите 'Завершить игру'.")

@bot.message_handler(commands=['showdown'])
def showdown(message):
    if not game_in_progress:
        bot.send_message(message.chat.id, "Сначала начните игру, нажав 'Играть в покер'.")
        return
    # Показываем карты всех игроков
    results = "Результаты игры:\n"
    for player_info in players.values():
        hand = ", ".join(player_info["hand"])
        results += f"{player_info['name']}: {hand}\n"
    bot.send_message(message.chat.id, results)
    end_game(message)

bot.polling()
