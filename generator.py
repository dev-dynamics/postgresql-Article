import csv
import random
from faker import Faker

fake = Faker('ru_RU')

def generate_dataset():
    print("Генерируем товары (50 000)...")
    categories = ['Электроника', 'Одежда', 'Дом', 'Книги', 'Спорт', 'Авто', 'Игры']
    with open('items.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['item_id', 'name', 'category', 'price'])
        for i in range(1, 50001):
            writer.writerow([i, fake.catch_phrase(), random.choice(categories), round(random.uniform(100, 50000), 2)])

    print("Генерируем пользователей (100 000)...")
    with open('users.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['user_id', 'city', 'age'])
        for i in range(1, 100001):
            writer.writerow([i, fake.city(), random.randint(18, 65)])

    print("Генерируем логи событий (1 000 000)...")
    with open('events.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['event_id', 'user_id', 'item_id', 'timestamp'])
        for i in range(1, 1000001):
            # Имитация «мусорного» поведения: некоторые пользователи кликают чаще
            user_id = random.randint(1, 1000) if random.random() > 0.3 else random.randint(1, 100000)
            item_id = random.randint(1, 500) if random.random() > 0.3 else random.randint(1, 50000)
            writer.writerow([i, user_id, item_id, fake.date_time_this_year().isoformat()])
            
    print("Готово! Данные сохранены в CSV.")

if __name__ == "__main__":
    generate_dataset()