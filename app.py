from fastapi import FastAPI
import psycopg2
from psycopg2 import pool
import redis
import asyncio
import sys
from concurrent.futures import ThreadPoolExecutor

# Фикс для Windows (Proactor позволяет обрабатывать больше соединений)
# if sys.platform == 'win32':
#     asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

app = FastAPI()

# Создаем пул соединений. 
# minconn=1, maxconn=50 (можно увеличить, если база позволяет)
# db_pool = psycopg2.pool.SimpleConnectionPool(
#     1, 50, 
#     dbname="kino", 
#     user="postgres", 
#     password="root", 
#     host="localhost"
# )

# Найти блок создания пула db_pool и обновить:
db_pool = psycopg2.pool.SimpleConnectionPool(
    1, 100,  # Увеличил maxconn до 100, так как Linux это легко переварит
    dbname="kino", 
    user="postgres", 
    password="root", 
    host="127.0.0.1", # В Linux лучше использовать 127.0.0.1 вместо localhost
    port="5432"
)

# Проверь подключение к Redis
# Если Redis запущен как service redis-server start, то настройки стандартные:
r = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)

# r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Экзекутор для запуска синхронных задач в отдельных потоках
executor = ThreadPoolExecutor(max_workers=100)

# # --- СТЕНД 1: Честный тяжелый SQL ---
# @app.get("/stand1")
# async def stand1(user_id: int):
#     conn = db_pool.getconn()
#     try:
#         with conn.cursor() as cur:
#             cur.execute("""
#                 SELECT i.name FROM items i 
#                 JOIN events e ON i.item_id = e.item_id 
#                 WHERE e.user_id = %s 
#                 GROUP BY i.name 
#                 ORDER BY count(e.event_id) DESC 
#                 LIMIT 10
#             """, (user_id,))
#             return cur.fetchall()
#     finally:
#         db_pool.putconn(conn)

# # --- СТЕНД 2: Чистый Redis (имитация кэша) ---
# @app.get("/stand2")
# async def stand2(user_id: int):
#     # Проверяем кэш
#     cache_key = f"user_res:{user_id}"
#     cached_data = r.get(cache_key)
    
#     if cached_data:
#         return {"source": "cache", "data": cached_data}
    
#     # Если в жизни кэша нет, мы бы шли в БД, но для теста 
#     # вернем "заглушку", как будто данные там всегда есть
#     return {"source": "cache", "data": ["Item 1", "Item 2", "Item 3"]}



#GOOD
@app.get("/stand1")
async def stand1(user_id: int):
    # Используем пул даже для тяжелого запроса
    conn = db_pool.getconn()
    try:
        loop = asyncio.get_running_loop()
        def heavy_query():
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT i.name FROM items i 
                    JOIN events e ON i.item_id = e.item_id 
                    WHERE e.user_id = %s 
                    GROUP BY i.name 
                    ORDER BY count(e.event_id) DESC 
                    LIMIT 10
                """, (user_id,))
                return cur.fetchall()
        
        # Запускаем в отдельном потоке, чтобы не вешать основной цикл FastAPI
        res = await loop.run_in_executor(executor, heavy_query)
        return res
    finally:
        db_pool.putconn(conn)


#LInux
@app.get("/stand2")
async def stand2(user_id: int):
    # Попытка достать из кэша (имитируем, что там лежит категория пользователя)
    category = r.get(f"user:{user_id}:fav") or "Электроника"
    
    conn = db_pool.getconn()
    try:
        loop = asyncio.get_running_loop()
        def fast_query():
            with conn.cursor() as cur:
                # В Стенде 2 делаем простой запрос по индексу, а не тяжелый JOIN
                cur.execute("SELECT name FROM items WHERE category = %s LIMIT 10", (category,))
                return cur.fetchall()
        
        res = await loop.run_in_executor(executor, fast_query)
        return res
    finally:
        db_pool.putconn(conn)

#GOOD
# @app.get("/stand2")
# async def stand2(user_id: int):
#     # 1. Быстрый запрос в Redis
#     # Redis-py поддерживает асинхронность не полностью в таком виде, 
#     # но для теста это не критично, так как он очень быстрый.
#     cat = r.get(f"user:{user_id}:fav") or "Электроника"
    
#     # 2. Берем соединение из пула
#     conn = db_pool.getconn()
#     try:
#         loop = asyncio.get_running_loop()
#         def fast_query():
#             with conn.cursor() as cur:
#                 cur.execute("SELECT name FROM items WHERE category = %s LIMIT 5", (cat,))
#                 return cur.fetchall()
        
#         res = await loop.run_in_executor(executor, fast_query)
#         return res
#     finally:
#         db_pool.putconn(conn)