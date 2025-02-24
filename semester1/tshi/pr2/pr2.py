import os
import telebot
from telebot import types
import sqlite3
import random
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN')
bot = telebot.TeleBot(TOKEN)

# Підключення до бази даних
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()

# Створення таблиць
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT,
                   phone TEXT,
                   unique_id INTEGER,
                   chat_id INTEGER
                )''')

# Створення таблиці з новою структурою
cursor.execute('''CREATE TABLE IF NOT EXISTS food_orders (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   user_id INTEGER,
                   food_name TEXT,
                   quantity INTEGER,
                   created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                   FOREIGN KEY(user_id) REFERENCES users(id)
                )''')


conn.commit()

# Словник для зберігання станів користувачів
user_states = {}

# Головне меню
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Замовити корм','Мої замовлення')
    markup.add('Погода', 'Конвертер валют')
    markup.add('Зареєструватись', 'Мій профіль')
    return markup

# Конфігурація для API
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
CURRENCY_API_URL = 'https://api.exchangerate-api.com/v4/latest/USD'

# Обробка старту та основного меню
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Вітаємо у боті для замовлення корму для декоративних тварин! Виберіть дію:", reply_markup=main_menu())

# Реєстрація користувача
@bot.message_handler(func=lambda message: message.text == 'Зареєструватись')
def register_start(message):
    # Check if user is already registered
    cursor.execute('SELECT * FROM users WHERE chat_id = ?', (message.chat.id,))
    existing_user = cursor.fetchone()
    
    if existing_user:
        bot.send_message(message.chat.id, "Ви вже зареєстровані в системі. Використайте 'Мій профіль' для перегляду даних.")
        return
    user_states[message.chat.id] = {'step': 'waiting_name'}
    bot.send_message(message.chat.id, "Введіть ваше ім'я:")

@bot.message_handler(func=lambda message: message.chat.id in user_states and user_states[message.chat.id]['step'] == 'waiting_name')
def process_name(message):
    user_states[message.chat.id]['name'] = message.text
    user_states[message.chat.id]['step'] = 'waiting_phone'
    bot.send_message(message.chat.id, "Введіть ваш номер телефону:")

@bot.message_handler(func=lambda message: message.chat.id in user_states and user_states[message.chat.id]['step'] == 'waiting_phone')
def process_phone(message):
    phone = message.text
    name = user_states[message.chat.id]['name']
    unique_id = random.randint(1000, 9999)
    
    cursor.execute('INSERT INTO users (name, phone, unique_id, chat_id) VALUES (?, ?, ?, ?)',
                  (name, phone, unique_id, message.chat.id))
    conn.commit()
    
    bot.send_message(message.chat.id, 
                    f"Реєстрація успішна!\nВаш ID: {unique_id}\nІм'я: {name}\nТелефон: {phone}",
                    reply_markup=main_menu())
    del user_states[message.chat.id]

# Перегляд профілю
@bot.message_handler(func=lambda message: message.text == 'Мій профіль')
def show_profile(message):
    cursor.execute('SELECT * FROM users WHERE chat_id = ?', (message.chat.id,))
    user = cursor.fetchone()
    if user:
        bot.send_message(message.chat.id, 
                        f"Ваш профіль:\nID: {user[3]}\nІм'я: {user[1]}\nТелефон: {user[2]}")
    else:
        bot.send_message(message.chat.id, "Ви не зареєстровані. Використайте команду 'Зареєструватись'")

# Погода
@bot.message_handler(func=lambda message: message.text == 'Погода')
def weather_start(message):
    user_states[message.chat.id] = {'step': 'waiting_city'}
    bot.send_message(message.chat.id, "Введіть назву міста:")

@bot.message_handler(func=lambda message: message.chat.id in user_states and user_states[message.chat.id]['step'] == 'waiting_city')
def process_weather(message):
    weather_info = get_weather(message.text)
    bot.send_message(message.chat.id, weather_info, reply_markup=main_menu())
    del user_states[message.chat.id]

# Конвертер валют
@bot.message_handler(func=lambda message: message.text == 'Конвертер валют')
def currency_start(message):
    user_states[message.chat.id] = {'step': 'waiting_amount'}
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Назад')
    bot.send_message(message.chat.id, "Введіть суму для конвертації:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.chat.id in user_states and user_states[message.chat.id]['step'] == 'waiting_amount')
def process_amount(message):
    if message.text == 'Назад':
        bot.send_message(message.chat.id, "Операцію скасовано", reply_markup=main_menu())
        del user_states[message.chat.id]
        return
    
    try:
        amount = float(message.text)
        user_states[message.chat.id]['amount'] = amount
        user_states[message.chat.id]['step'] = 'waiting_from_currency'
        bot.send_message(message.chat.id, "Введіть вихідну валюту (наприклад, USD):")
    except ValueError:
        bot.send_message(message.chat.id, "Будь ласка, введіть коректне число")

@bot.message_handler(func=lambda message: message.chat.id in user_states and user_states[message.chat.id]['step'] == 'waiting_from_currency')
def process_from_currency(message):
    if message.text == 'Назад':
        bot.send_message(message.chat.id, "Операцію скасовано", reply_markup=main_menu())
        del user_states[message.chat.id]
        return
    
    user_states[message.chat.id]['from_currency'] = message.text.upper()
    user_states[message.chat.id]['step'] = 'waiting_to_currency'
    bot.send_message(message.chat.id, "Введіть цільову валюту (наприклад, EUR):")

@bot.message_handler(func=lambda message: message.chat.id in user_states and user_states[message.chat.id]['step'] == 'waiting_to_currency')
def process_to_currency(message):
    if message.text == 'Назад':
        bot.send_message(message.chat.id, "Операцію скасовано", reply_markup=main_menu())
        del user_states[message.chat.id]
        return
    
    state = user_states[message.chat.id]
    result = convert_currency(state['amount'], state['from_currency'], message.text.upper())
    bot.send_message(message.chat.id, result, reply_markup=main_menu())
    del user_states[message.chat.id]

# Функція для запиту погоди
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    print(response)
    if response.status_code == 200:
        data = response.json()
        return f"Погода в {city}:\nТемпература: {data['main']['temp']}°C\nОпис: {data['weather'][0]['description']}"
    elif response.status_code == 429:
        return "Перевищено ліміт запитів. Будь ласка, спробуйте пізніше."
    else:
        return "Місто не знайдено. Спробуйте ще раз."

# Функція для конвертації валют
def convert_currency(amount, from_currency, to_currency):
    response = requests.get(CURRENCY_API_URL)
    if response.status_code == 200:
        rates = response.json()['rates']
        if from_currency in rates and to_currency in rates:
            converted = amount / rates[from_currency] * rates[to_currency]
            return f"{amount} {from_currency} = {converted:.2f} {to_currency}"
        else:
            return "Одна з валют не підтримується."
    else:
        return "Помилка отримання даних. Спробуйте пізніше."
@bot.message_handler(func=lambda message: message.text == 'Переглянути корм')
def view_food(message):
    bot.send_message(message.chat.id, "Ось список доступного корму:\n1. Корм для гризунів\n2. Корм для рибок\n3. Корм для птахів", reply_markup=main_menu())


# Замовлення корму
@bot.message_handler(func=lambda message: message.text == 'Замовити корм')
def order_food(message):
    # Перевірка чи користувач зареєстрований
    cursor.execute('SELECT id FROM users WHERE chat_id = ?', (message.chat.id,))
    user = cursor.fetchone()
    
    if not user:
        bot.send_message(message.chat.id, "Спочатку потрібно зареєструватися!", reply_markup=main_menu())
        return
        
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Корм для гризунів', 'Корм для рибок', 'Корм для птахів')
    markup.add('Назад')
    bot.send_message(message.chat.id, "Виберіть тип корму:", reply_markup=markup)
    user_states[message.chat.id] = {'step': 'waiting_food_type'}

@bot.message_handler(func=lambda message: message.chat.id in user_states and user_states[message.chat.id]['step'] == 'waiting_food_type')
def handle_food_type(message):
    if message.text == 'Назад':
        bot.send_message(message.chat.id, "Повернення до головного меню", reply_markup=main_menu())
        del user_states[message.chat.id]
        return
        
    if message.text in ['Корм для гризунів', 'Корм для рибок', 'Корм для птахів']:
        user_states[message.chat.id] = {'step': 'waiting_quantity', 'food_name': message.text}
        bot.send_message(message.chat.id, "Введіть кількість упаковок (від 1 до 10):")
    else:
        bot.send_message(message.chat.id, "Будь ласка, виберіть корм із запропонованих варіантів")

@bot.message_handler(func=lambda message: message.chat.id in user_states and user_states[message.chat.id]['step'] == 'waiting_quantity')
def handle_food_order(message):
    try:
        quantity = int(message.text)
        if not 1 <= quantity <= 10:
            raise ValueError("Кількість повинна бути від 1 до 10")
            
        # Отримуємо user_id
        cursor.execute('SELECT id FROM users WHERE chat_id = ?', (message.chat.id,))
        user = cursor.fetchone()
        
        # Зберігаємо замовлення в базі даних
        cursor.execute('INSERT INTO food_orders (user_id, food_name, quantity) VALUES (?, ?, ?)',
                      (user[0], user_states[message.chat.id]['food_name'], quantity))
        conn.commit()
        
        bot.send_message(
            message.chat.id, 
            f"Ваше замовлення на {quantity} упаковок '{user_states[message.chat.id]['food_name']}' успішно збережено!",
            reply_markup=main_menu()
        )
        del user_states[message.chat.id]
        
    except ValueError as e:
        if str(e) == "Кількість повинна бути від 1 до 10":
            bot.send_message(message.chat.id, str(e))
        else:
            bot.send_message(message.chat.id, "Будь ласка, введіть коректне число")
    except Exception as e:
        bot.send_message(message.chat.id, "Сталася помилка при оформленні замовлення. Спробуйте ще раз.", reply_markup=main_menu())
        del user_states[message.chat.id]

# Консультація
@bot.message_handler(func=lambda message: message.text == 'Консультація щодо корму')
def consultation_handler(message):
    bot.send_message(message.chat.id, "Напишіть ваше питання, і ми зв’яжемося з вами якнайшвидше.", reply_markup=main_menu())



# Додаємо новий обробник для перегляду замовлень
@bot.message_handler(func=lambda message: message.text == 'Мої замовлення')
def show_orders(message):
    # Перевіряємо чи користувач зареєстрований
    cursor.execute('SELECT id FROM users WHERE chat_id = ?', (message.chat.id,))
    user = cursor.fetchone()
    
    if not user:
        bot.send_message(message.chat.id, "Спочатку потрібно зареєструватися!", reply_markup=main_menu())
        return

    # Отримуємо всі замовлення користувача
    cursor.execute('''
        SELECT food_name, quantity, datetime(created_at, 'localtime') 
        FROM food_orders 
        WHERE user_id = ? 
        ORDER BY created_at DESC
        LIMIT 10
    ''', (user[0],))
    
    orders = cursor.fetchall()
    
    if not orders:
        bot.send_message(message.chat.id, "У вас поки немає замовлень.", reply_markup=main_menu())
        return

    # Формуємо повідомлення зі списком замовлень
    message_text = "Ваші останні замовлення:\n\n"
    for i, (food_name, quantity, order_date) in enumerate(orders, 1):
        message_text += f"{i}. {food_name} - {quantity} шт.\n   Дата: {order_date}\n\n"
    
    bot.send_message(message.chat.id, message_text, reply_markup=main_menu())
# Обробка невідомих повідомлень
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    if message.text == 'Назад':
        bot.send_message(message.chat.id, "Повернення до головного меню", reply_markup=main_menu())
        if message.chat.id in user_states:
            del user_states[message.chat.id]
    else:
        bot.send_message(message.chat.id, "Не розумію команду. Використовуйте меню для навігації.", reply_markup=main_menu())

bot.polling(none_stop=True)