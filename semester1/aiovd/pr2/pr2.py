import kagglehub
import pandas as pd
import matplotlib.pyplot as plt

# Завантаження датасету з Kaggle
path = kagglehub.dataset_download("kaggle/us-baby-names")

# Шлях до файлу NationalNames.csv
file_path = f"{path}/NationalNames.csv"

# Завантаження даних у DataFrame
data = pd.read_csv(file_path)

# 1. Виведіть перші 8 рядків набору даних.
print("\n1. Виведіть перші 8 рядків набору даних.")
print(data.head(8))

# 2. Виведіть останні 8 рядків набору даних.
print("\n2. Виведіть останні 8 рядків набору даних.")
print(data.tail(8))

# 4. Отримайте загальну інформацію про дані у наборі даних.
print("\n4. Отримайте загальну інформацію про дані у наборі даних.")
print(data.info())

# 5. Знайдіть кількість унікальних імен у наборі даних.
print("\n5. Знайдіть кількість унікальних імен у наборі даних.")
unique_names = data['Name'].nunique()
print(f"Кількість унікальних імен: {unique_names}")

# 6. Обчисліть кількість унікальних жіночих та чоловічих імен.
print("\n6. Обчисліть кількість унікальних жіночих та чоловічих імен.")
unique_female_names = data[data['Gender'] == 'F']['Name'].nunique()
unique_male_names = data[data['Gender'] == 'M']['Name'].nunique()
print(f"Унікальні жіночі імена: {unique_female_names}")
print(f"Унікальні чоловічі імена: {unique_male_names}")

# 7. Знайдіть 5 найпопулярніших чоловічих імен у 2010 році.
print("\n7. Знайдіть 5 найпопулярніших чоловічих імен у 2010 році.")
male_2010 = data[(data['Gender'] == 'M') & (data['Year'] == 2010)]
top_5_male_2010 = male_2010.groupby('Name')['Count'].sum().sort_values(ascending=False).head(5)
print(top_5_male_2010)

# 8. Найпопулярніше ім’я за один рік (максимальне Count).
max_name = data.loc[data['Count'].idxmax()]
print("Найпопулярніше ім’я за результатами одного року:")
print(max_name)

# 9. Кількість записів із мінімальним Count.
min_count = data['Count'].min()
min_count_records = data[data['Count'] == min_count].shape[0]
print(f"\n9. Кількість записів із мінімальним Count ({min_count}): {min_count_records}")

# 10. Кількість унікальних імен у кожному році.
unique_names_per_year = data.groupby('Year')['Name'].nunique()
print("\n10. Кількість унікальних імен у кожному році.")
print(unique_names_per_year)

# 11. Рік із найбільшою кількістю унікальних імен.
year_max_unique_names = unique_names_per_year.idxmax()
print(f"\n11. Рік із найбільшою кількістю унікальних імен: {year_max_unique_names}")

# 12. Найпопулярніше ім’я у році з найбільшою кількістю унікальних імен.
most_popular_in_max_year = data[data['Year'] == year_max_unique_names].groupby('Name')['Count'].sum().idxmax()
print(f"\n12. Найпопулярніше ім’я у {year_max_unique_names} році: {most_popular_in_max_year}")

# 18. Кількість років, коли дівчаток народжувалось більше, ніж хлопчиків.
births_by_gender = data.groupby(['Year', 'Gender'])['Count'].sum().unstack()
years_more_females = (births_by_gender['F'] > births_by_gender['M']).sum()
print(f"\n18. Кількість років, коли дівчаток народжувалось більше, ніж хлопчиків: {years_more_females}")

# 19. Графік загальної кількості народжень хлопчиків та дівчаток на рік.
births_by_gender.plot(kind='line', figsize=(10, 6))
plt.title("19. Кількість народжень хлопчиків та дівчаток на рік")
plt.xlabel("Рік")
plt.ylabel("Кількість народжень")
plt.legend(['Дівчатка', 'Хлопчики'])
plt.show()

# 20. Кількість гендерно-нейтральних імен.
gender_neutral_names = data.groupby('Name')['Gender'].nunique()
neutral_count = (gender_neutral_names == 2).sum()
print(f"\n20. Кількість гендерно-нейтральних імен: {neutral_count}")

# 21. Кількість хлопчиків з ім’ям Barbara.
barbara_count = data[(data['Name'] == 'Barbara') & (data['Gender'] == 'M')]['Count'].sum()
print(f"\n21. Кількість хлопчиків із ім’ям Barbara: {barbara_count}")

# 23. Найпопулярніші гендерно-нейтральні імена (присутні кожного року).
neutral_names = gender_neutral_names[gender_neutral_names == 2].index
popular_neutral_names = data[data['Name'].isin(neutral_names)].groupby('Name')['Count'].sum().sort_values(ascending=False).head(5)
print("\n23. Найпопулярніші гендерно-нейтральні імена:")
print(popular_neutral_names)

# 25. Графіки для імен John та Mary.
plt.figure(figsize=(12, 6))

# Plot for John and Mary
john_data = data[data['Name'] == 'John'].groupby('Year')['Count'].sum()
mary_data = data[data['Name'] == 'Mary'].groupby('Year')['Count'].sum()

plt.plot(john_data.index, john_data.values, label='John')
plt.plot(mary_data.index, mary_data.values, label='Mary')

plt.title("25. Розподілення кількості імен John та Mary по роках")
plt.xlabel("Рік")
plt.ylabel("Кількість")
plt.legend()

plt.tight_layout()
plt.show()


# 27. Найпопулярніші імена в кожному році.
popular_names_by_year = data.loc[data.groupby('Year')['Count'].idxmax(), ['Year', 'Name', 'Count']]
print("\n27. Найпопулярніші імена в кожному році:")
print(popular_names_by_year)
