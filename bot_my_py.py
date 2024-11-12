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
community_cards = []
pot = 0  # банк для ставок

# Функция для создания клавиатуры
def create_keyboard(start_game=False):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if start_game:
        button_ready = types.KeyboardButton('Начать раздачу')  # Кнопка для начала раздачи карт
        markup.add(button_ready)
    else:
        button_play = types.KeyboardButton('Играть в покер')  # Кнопка для начала игры
        button_end = types.KeyboardButton('Завершить игру')   # Кнопка для завершения игры
        markup.add(button_play, button_end)
    return markup

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Добро пожаловать! Нажмите 'Играть в покер', чтобы начать игру или 'Завершить игру', чтобы выйти.", reply_markup=create_keyboard())

@bot.message_handler(func=lambda message: message.text == 'Играть в покер')
def start_game(message):
    global game_in_progress, players, deck, community_cards, pot
    if game_in_progress:
        bot.send_message(message.chat.id, "Игра уже идет! Чтобы начать новую игру, сначала завершите текущую.")
    else:
        game_in_progress = True
        players = {}  # Сбросим список игроков
        deck = [f"{rank}{suit}" for suit in suits for rank in ranks]
        random.shuffle(deck)
        community_cards = []  # Сбросим карты на столе
        pot = 0  # Сбросим банк
        bot.send_message(message.chat.id, "Игра началась! Введите /join, чтобы присоединиться. Когда все будут готовы, нажмите 'Начать раздачу'.", reply_markup=create_keyboard(start_game=True))

@bot.message_handler(commands=['join'])
def join_game(message):
    global players
    if not game_in_progress:
        bot.send_message(message.chat.id, "Сначала начните игру, нажав 'Играть в покер'.")
        return
    if message.from_user.id in players:
        bot.send_message(message.chat.id, f"{message.from_user.first_name}, вы уже присоединились!")
    else:
        players[message.from_user.id] = {"name": message.from_user.first_name, "hand": [], "bet": 0}
        bot.send_message(message.chat.id, f"{message.from_user.first_name} присоединился к игре!")
        notify_players_joined()

def notify_players_joined():
    player_names = [info["name"] for info in players.values()]
    bot.send_message(list(players.keys())[0], f"Игроки, присоединившиеся к игре: {', '.join(player_names)}")

@bot.message_handler(func=lambda message: message.text == 'Начать раздачу')
def start_deal(message):
    global players, game_in_progress, community_cards
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
    
    # Начинаем первый раунд - выкладываем флоп
    community_cards = [deck.pop() for _ in range(3)]
    bot.send_message(message.chat.id, f"Флоп: {', '.join(community_cards)}")
    bot.send_message(message.chat.id, "Сделайте ваши ставки! Используйте команду /bet <сумма>.")

@bot.message_handler(commands=['bet'])
def place_bet(message):
    global pot
    if not game_in_progress:
        bot.send_message(message.chat.id, "Сначала начните игру, нажав 'Играть в покер'.")
        return

    try:
        bet_amount = int(message.text.split()[1])
    except (IndexError, ValueError):
        bot.send_message(message.chat.id, "Введите ставку в формате /bet <сумма>.")
        return

    if bet_amount <= 0:
        bot.send_message(message.chat.id, "Ставка должна быть больше нуля.")
        return

    player = players.get(message.from_user.id)
    if player:
        player['bet'] = bet_amount
        pot += bet_amount
        bot.send_message(message.chat.id, f"{player['name']} поставил {bet_amount}. Общий банк: {pot}")
    else:
        bot.send_message(message.chat.id, "Сначала присоединитесь к игре, используя команду /join.")

@bot.message_handler(commands=['next'])
def next_round(message):
    global community_cards, deck
    if not game_in_progress:
        bot.send_message(message.chat.id, "Сначала начните игру, нажав 'Играть в покер'.")
        return
    if len(community_cards) == 3:
        # Выкладываем терн
        community_cards.append(deck.pop())
        bot.send_message(message.chat.id, f"Тёрн: {', '.join(community_cards)}")
    elif len(community_cards) == 4:
        # Выкладываем ривер
        community_cards.append(deck.pop())
        bot.send_message(message.chat.id, f"Ривер: {', '.join(community_cards)}")
        bot.send_message(message.chat.id, "Игра завершена! Используйте команду /showdown для показа карт.")
    else:
        bot.send_message(message.chat.id, "Карты на столе уже выложены.")

@bot.message_handler(commands=['showdown'])
def showdown(message):
    global game_in_progress
    if not game_in_progress:
        bot.send_message(message.chat.id, "Сначала начните игру, нажав 'Играть в покер'.")
        return
    # Показываем карты всех игроков
    results = "Результаты игры:\n"
    for player_info in players.values():
        hand = ", ".join(player_info["hand"])
        results += f"{player_info['name']}: {hand}\n"
    results += f"Общие карты: {', '.join(community_cards)}"
    bot.send_message(message.chat.id, results)
    end_game(message)

@bot.message_handler(func=lambda message: message.text == 'Завершить игру')
def end_game(message):
    global game_in_progress, players, community_cards, pot
    game_in_progress = False
    players = {}
    community_cards = []
    pot = 0
    bot.send_message(message.chat.id, "Игра завершена! Нажмите 'Играть в покер' для новой игры.", reply_markup=create_keyboard())

bot.polling()
