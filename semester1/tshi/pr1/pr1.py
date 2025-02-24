import telebot
from telebot import types
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN')
bot = telebot.TeleBot(TOKEN)

# Dictionary to store user order states
user_orders = {}

# Головне меню з кнопками
def main_menu():
    menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
    menu.add(types.KeyboardButton("Замовити корм"))
    menu.add(types.KeyboardButton("Деталі про корм"))
    menu.add(types.KeyboardButton("Акції"))
    menu.add(types.KeyboardButton("Контакти"))
    return menu

# Відправка головного меню
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Ласкаво просимо до сервісу замовлення корму для декоративних тварин! Оберіть дію:",
        reply_markup=main_menu()
    )

# Обробка замовлення корму
@bot.message_handler(func=lambda message: message.text == "Замовити корм")
def order_food(message):
    user_orders[message.chat.id] = {'step': 'choosing_type'}
    options = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    options.add("Для гризунів", "Для рибок", "Для птахів", "Спеціальне замовлення")
    bot.send_message(
        message.chat.id,
        "Оберіть тип корму:",
        reply_markup=options
    )

# Обробка вибору типу корму
@bot.message_handler(func=lambda message: message.chat.id in user_orders and user_orders[message.chat.id]['step'] == 'choosing_type')
def handle_food_type(message):
    if message.text in ["Для гризунів", "Для рибок", "Для птахів", "Спеціальне замовлення"]:
        user_orders[message.chat.id]['food_type'] = message.text
        user_orders[message.chat.id]['step'] = 'choosing_quantity'
        
        quantity_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        quantity_markup.add("1 кг", "2 кг", "5 кг", "Інша кількість")
        
        bot.send_message(
            message.chat.id,
            "Оберіть кількість корму:",
            reply_markup=quantity_markup
        )
    else:
        bot.send_message(
            message.chat.id,
            "Будь ласка, оберіть тип корму з представлених варіантів."
        )

# Обробка вибору кількості
@bot.message_handler(func=lambda message: message.chat.id in user_orders and user_orders[message.chat.id]['step'] == 'choosing_quantity')
def handle_quantity(message):
    user_orders[message.chat.id]['quantity'] = message.text
    user_orders[message.chat.id]['step'] = 'confirming'
    
    confirm_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    confirm_markup.add("Підтвердити", "Скасувати")
    
    order_summary = f"Ваше замовлення:\nТип корму: {user_orders[message.chat.id]['food_type']}\nКількість: {message.text}\n\nБажаєте підтвердити замовлення?"
    
    bot.send_message(
        message.chat.id,
        order_summary,
        reply_markup=confirm_markup
    )

# Обробка підтвердження замовлення
@bot.message_handler(func=lambda message: message.chat.id in user_orders and user_orders[message.chat.id]['step'] == 'confirming')
def handle_confirmation(message):
    if message.text == "Підтвердити":
        order_details = user_orders[message.chat.id]
        confirmation_message = f"Дякуємо за замовлення!\n\nДеталі замовлення:\nТип корму: {order_details['food_type']}\nКількість: {order_details['quantity']}\n\nМи зв'яжемося з вами найближчим часом для уточнення деталей доставки."
        bot.send_message(
            message.chat.id,
            confirmation_message,
            reply_markup=main_menu()
        )
    elif message.text == "Скасувати":
        bot.send_message(
            message.chat.id,
            "Замовлення скасовано. Повертаємось до головного меню.",
            reply_markup=main_menu()
        )
    
    # Clear the order state
    if message.chat.id in user_orders:
        del user_orders[message.chat.id]

# Інформація про корм
@bot.message_handler(func=lambda message: message.text == "Деталі про корм")
def food_details(message):
    bot.send_message(message.chat.id, "Наш корм виготовляється з натуральних інгредієнтів, адаптованих до потреб ваших тварин. Ви можете дізнатись більше, запитавши конкретний тип.")

# Акції
@bot.message_handler(func=lambda message: message.text == "Акції")
def sales(message):
    bot.send_message(message.chat.id, "Сьогодні діють такі знижки:\n- Корм для гризунів: -20%\n- Корм для птахів: -15%\nНе пропустіть нагоду!")

# Контакти
@bot.message_handler(func=lambda message: message.text == "Контакти")
def contacts(message):
    bot.send_message(
        message.chat.id,
        "Контакти:\nТелефон: +380 (XX) XXX-XXXX\nEmail: petfood@example.com\nАдреса: вул. Декоративна, 21"
    )

# Довідка
@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(
        message.chat.id,
        "Ось список команд:\n/start - Почати роботу\n/help - Довідка\n/buttons - Демонстрація кнопок"
    )

bot.polling(none_stop=True)
