import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

columns = ['symboling', 'normalized-losses', 'make', 'fuel-type', 'aspiration', 'num-of-doors', 
           'body-style', 'drive-wheels', 'engine-location', 'wheel-base', 'length', 'width', 
           'height', 'curb-weight', 'engine-type', 'num-of-cylinders', 'engine-size', 
           'fuel-system', 'bore', 'stroke', 'compression-ratio', 'horsepower', 'peak-rpm', 
           'city-mpg', 'highway-mpg', 'price']

df = pd.read_csv('imports-85.data', names=columns)

# 2.1 Заміна NaN у стовпці 'stroke' середнім значенням
df['stroke'] = pd.to_numeric(df['stroke'].replace('?', np.nan))
stroke_mean = df['stroke'].mean()
df['stroke'] = df['stroke'].fillna(stroke_mean)

# 2.2 Нормалізація стовпця 'height'
scaler = MinMaxScaler()
df['height'] = pd.to_numeric(df['height'])
df['height_normalized'] = scaler.fit_transform(df[['height']])

# 2.2.1 Створення індикаторної змінної для стовпця 'aspiration'
aspiration_dummies = pd.get_dummies(df['aspiration'], prefix='aspiration')

# 2.2.2 Об'єднання з вихідним фреймом та видалення стовпця 'aspiration'
df = pd.concat([df, aspiration_dummies], axis=1)
df = df.drop('aspiration', axis=1)

# 2.3 Заміна всіх NaN у всіх стовпцях середнім значенням
# Спочатку замінимо '?' на NaN
df = df.replace('?', np.nan)

# Конвертуємо числові стовпці
numeric_columns = df.select_dtypes(include=[np.number]).columns
for col in df.columns:
    if col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# Заповнюємо NaN середніми значеннями для числових стовпців
for col in numeric_columns:
    df[col] = df[col].fillna(df[col].mean())

# Для категоріальних стовпців заповнюємо NaN найчастішим значенням
categorical_columns = df.select_dtypes(include=['object']).columns
for col in categorical_columns:
    df[col] = df[col].fillna(df[col].mode()[0])

print("Розмір датафрейму після обробки:", df.shape)
print("\nПерші 5 рядків обробленого датафрейму:")
print(df.head())
print("\nІнформація про датафрейм:")
print(df.info())