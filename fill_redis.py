import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

print("Заполняем Redis категориями для юзеров...")
categories = ['Электроника', 'Одежда', 'Дом', 'Книги', 'Спорт']

# Для первых 100 000 пользователей назначим случайную "любимую" категорию
pipe = r.pipeline()
for user_id in range(1, 100001):
    pipe.set(f"user:{user_id}:fav", categories[user_id % 5])
    if user_id % 10000 == 0:
        pipe.execute()
        print(f"Загружено {user_id}...")
print("Redis готов!")