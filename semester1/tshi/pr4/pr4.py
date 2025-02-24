import asyncio
import logging
import sqlite3
import requests

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    ContentType,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from dotenv import load_dotenv
import os

load_dotenv()
# ------------------ Налаштування логування ------------------ #
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# ------------------ Ваш токен бота ------------------ #
BOT_TOKEN = os.getenv('TOKEN')

# ------------------ Приклад API-ключа для OpenWeather (необов'язково) ------------------ #
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
# ------------------ Налаштування / створення SQLite БД ------------------ #
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    username TEXT,
    full_name TEXT,
    favorite_brand TEXT,
    favorite_color TEXT
);
""")
conn.commit()


async def cmd_start(message: Message) -> None:
    """
    Обробник команди /start
    """
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name

    # Перевіримо, чи існує користувач у БД
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()

    # Якщо немає – створимо запис
    if not user:
        cursor.execute(
            "INSERT INTO users (user_id, username, full_name) VALUES (?, ?, ?)",
            (user_id, username, full_name),
        )
        conn.commit()

    await message.answer(
        "Привіт! Я бот для підбору квадроцикла.\n"
        "Надішліть /help, щоб дізнатися, що я вмію."
    )


async def cmd_help(message: Message) -> None:
    """
    Обробник команди /help
    """
    help_text = (
        "Список команд:\n"
        "/start - Почати роботу\n"
        "/help - Допомога\n"
        "/weather - Перевірити погоду\n"
        "/select_brand - Обрати бренд квадроцикла\n"
        "/select_color - Обрати колір квадроцикла\n"
    )
    await message.answer(help_text)


async def cmd_weather(message: Message) -> None:
    """
    Приклад отримання погоди через OpenWeatherMap
    """
    city = "Kyiv"
    url = (
        f"https://api.openweathermap.org/data/2.5/weather?"
        f"q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ua"
    )

    try:
        response = requests.get(url)
        data = response.json()
        # Перевіримо код відповіді
        if data.get("cod") != 200:
            await message.answer("Не вдалося отримати інформацію про погоду.")
            return

        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        await message.answer(
            f"Погода в {city} зараз:\n"
            f"Температура: {temp}°C\n"
            f"Опис: {desc}"
        )
    except Exception as e:
        logging.exception("Помилка при отриманні погоди:")
        await message.answer("Сталася помилка при отриманні погоди.")


async def cmd_select_brand(message: Message) -> None:
    """
    Приклад використання Reply-клавіатури для вибору бренда
    """
    kb_builder = ReplyKeyboardBuilder()
    brands = ["Polaris", "Can-Am", "Yamaha", "Honda"]
    for brand in brands:
        kb_builder.button(text=brand)
    kb_builder.adjust(2)  # 2 кнопки в один ряд

    keyboard = kb_builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
    await message.answer("Оберіть бренд квадроцикла:", reply_markup=keyboard)


async def cmd_select_color(message: Message) -> None:
    """
    Приклад використання Inline-кнопок для вибору кольору
    """
    kb_builder = InlineKeyboardBuilder()
    colors = ["Червоний", "Синій", "Зелений", "Чорний"]
    for color in colors:
        cb_data = f"color_{color.lower()}"
        kb_builder.button(
            text=color,
            callback_data=cb_data
        )
    kb_builder.adjust(2)

    await message.answer(
        "Оберіть колір квадроцикла:",
        reply_markup=kb_builder.as_markup()
    )


async def callback_color(call: CallbackQuery) -> None:
    """
    Обробка натискання інлайн-кнопок кольору
    """
    # Витягнемо колір
    raw_color = call.data.replace("color_", "")
    color = raw_color.capitalize()

    # Збережемо у БД
    user_id = call.from_user.id
    cursor.execute(
        "UPDATE users SET favorite_color = ? WHERE user_id = ?",
        (color, user_id)
    )
    conn.commit()

    # Відповідь користувачу
    await call.message.answer(f"Ви обрали колір: {color}")
    await call.answer()  # Закрити "годинник" на кнопці


async def text_handler(message: Message) -> None:
    """
    Загальна обробка будь-яких інших текстових повідомлень
    """
    user_text = message.text.strip()

    # Перевіримо, чи це один із брендів
    possible_brands = ["Polaris", "Can-Am", "Yamaha", "Honda"]
    if user_text in possible_brands:
        user_id = message.from_user.id
        cursor.execute(
            "UPDATE users SET favorite_brand = ? WHERE user_id = ?",
            (user_text, user_id)
        )
        conn.commit()
        await message.answer(f"Ви обрали бренд: {user_text}")
    else:
        # Якщо це не бренд, то просто відповідаємо загальним текстом
        await message.answer(
            "Я отримав ваше повідомлення, але не зовсім розумію.\n"
            "Спробуйте обрати команду чи скористатися меню."
        )


async def photo_handler(message: Message) -> None:
    """
    Обробка отриманого фото
    """
    # Можна зберегти його file_id, скачати чи виконати інші дії.
    await message.answer("Дякую за фото! Я можу зберегти його для подальшої обробки.")


async def main():
    # Створюємо бот і диспетчер
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Реєструємо хендлери для команд
    dp.message.register(cmd_start, Command(commands=["start"]))
    dp.message.register(cmd_help, Command(commands=["help"]))
    dp.message.register(cmd_weather, Command(commands=["weather"]))
    dp.message.register(cmd_select_brand, Command(commands=["select_brand"]))
    dp.message.register(cmd_select_color, Command(commands=["select_color"]))

    # Обробка inline callback
    dp.callback_query.register(callback_color, F.data.startswith("color_"))

    # Обробка фото
    dp.message.register(photo_handler, F.content_type == ContentType.PHOTO)

    # Обробка будь-якого іншого тексту (зверніть увагу, що має бути вкінці)
    dp.message.register(text_handler, F.text)

    try:
        logging.info("Бот запущено. Очікуємо повідомлень...")
        await dp.start_polling(bot)
    except Exception as err:
        logging.exception("Помилка при запуску бота:")
    finally:
        # Закриваємо підключення до БД при зупинці
        conn.close()


if __name__ == "__main__":
    asyncio.run(main())
