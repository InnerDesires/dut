import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import LabeledPrice, PreCheckoutQuery, Message
import asyncio
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('TOKEN')
PAYMENT_TOKEN = os.getenv('PAYMENT_TOKEN')  # Move payment token to .env

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Product catalog
PRODUCTS = {
    'cat_food_premium': {
        'title': 'Premium Cat Food',
        'description': 'Premium quality cat food with salmon (2kg)',
        'price': 2500,  # $25.00
        'photo_url': 'https://example.com/cat_food.jpg',
    },
    'dog_food_premium': {
        'title': 'Premium Dog Food',
        'description': 'Premium quality dog food with beef (3kg)',
        'price': 3000,  # $30.00
        'photo_url': 'https://example.com/dog_food.jpg',
    },
    'small_pet_food': {
        'title': 'Small Pet Food Mix',
        'description': 'Special mix for small pets (1kg)',
        'price': 1500,  # $15.00
        'photo_url': 'https://example.com/small_pet_food.jpg',
    }
}

def get_main_keyboard():
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton(text='🛍 Каталог'),
                types.KeyboardButton(text='🛒 Мої замовлення')
            ],
            [
                types.KeyboardButton(text='ℹ️ Про магазин'),
                types.KeyboardButton(text='📞 Контакти')
            ],
            [types.KeyboardButton(text='💬 Підтримка')]
        ],
        resize_keyboard=True,
        input_field_placeholder="Оберіть опцію з меню"
    )

def get_catalog_keyboard():
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text='🐱 Premium Cat Food - $25',
                    callback_data='buy_cat_food_premium'
                )
            ],
            [
                types.InlineKeyboardButton(
                    text='🐕 Premium Dog Food - $30',
                    callback_data='buy_dog_food_premium'
                )
            ],
            [
                types.InlineKeyboardButton(
                    text='🐹 Small Pet Food Mix - $15',
                    callback_data='buy_small_pet_food'
                )
            ]
        ]
    )

@dp.message(Command('start'))
async def start_cmd(message: types.Message):
    await message.answer(
        "👋 Ласкаво просимо до Pet Food Store!\n\n"
        "🔸 Преміум корми для ваших улюбленців\n"
        "🔸 Безпечна оплата\n"
        "🔸 Швидка доставка\n\n"
        "Оберіть опцію в меню:",
        reply_markup=get_main_keyboard()
    )

@dp.message(F.text == '🛍 Каталог')
async def show_catalog(message: types.Message):
    await message.answer(
        "Оберіть товар з нашого каталогу:",
        reply_markup=get_catalog_keyboard()
    )

@dp.callback_query(F.data.startswith('buy_'))
async def process_buy(callback: types.CallbackQuery):
    product_id = callback.data.replace('buy_', '')
    product = PRODUCTS.get(product_id)
    
    if not product:
        await callback.answer("Товар не знайдено")
        return

    await bot.send_invoice(
        chat_id=callback.message.chat.id,
        title=product['title'],
        description=product['description'],
        payload=product_id,
        provider_token=PAYMENT_TOKEN,
        currency='USD',
        prices=[
            LabeledPrice(
                label=product['title'],
                amount=product['price']
            )
        ],
        photo_url=product['photo_url'],
        photo_height=512,
        photo_width=512,
        photo_size=512,
        need_shipping_address=True,
        need_phone_number=True,
        protect_content=False
    )
    await callback.answer()

@dp.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message(F.successful_payment)
async def process_successful_payment(message: Message):
    total_amount = message.successful_payment.total_amount // 100
    currency = message.successful_payment.currency
    
    await message.answer(
        f"✅ Дякуємо за покупку!\n\n"
        f"💰 Оплачено: {total_amount} {currency}\n"
        f"🚚 Ваше замовлення буде відправлено найближчим часом.\n\n"
        f"📦 Номер замовлення: {message.successful_payment.invoice_payload}"
    )

@dp.message(F.text == 'ℹ️ Про магазин')
async def about_store(message: types.Message):
    await message.answer(
        "🏪 Pet Food Store - ваш надійний постачальник кормів!\n\n"
        "🏆 Офіційний дистриб'ютор преміум брендів\n"
        "✅ Гарантія якості\n"
        "🚚 Доставка по всій країні\n"
        "💯 Тисячі задоволених клієнтів"
    )

@dp.message(F.text == '📞 Контакти')
async def contacts(message: types.Message):
    await message.answer(
        "📞 Наші контакти:\n\n"
        "☎️ Телефон: +380XXXXXXXXX\n"
        "📧 Email: support@petfoodstore.com\n"
        "🌐 Веб-сайт: www.petfoodstore.com\n"
        "📍 Адреса: вул. Центральна, 123"
    )

@dp.message(F.text == '💬 Підтримка')
async def support(message: types.Message):
    await message.answer(
        "Служба підтримки працює 24/7\n\n"
        "📞 Гаряча лінія: 0800 XXX XXX\n"
        "💌 Email: help@petfoodstore.com\n\n"
        "Середній час відповіді: 15 хвилин"
    )

@dp.message(F.text == '🛒 Мої замовлення')
async def my_orders(message: types.Message):
    await message.answer(
        "Для перегляду ваших замовлень:\n\n"
        "1️⃣ Відвідайте наш веб-сайт\n"
        "2️⃣ Увійдіть в особистий кабінет\n"
        "3️⃣ Перейдіть у розділ 'Мої замовлення'"
    )

if __name__ == '__main__':
    asyncio.run(dp.start_polling(bot))
