# Видалення існуючої таблиці food_orders

import sqlite3

# Підключення до бази даних
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('DROP TABLE IF EXISTS food_orders')

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