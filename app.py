from fastapi import FastAPI
import psycopg2
import redis
import asyncio#
import sys#

if sys.platform == 'win32':#
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())#

app = FastAPI()
# Подключения (проверь свои данные)
db = psycopg2.connect(dbname="kino", user="postgres", password="root", host="localhost")
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

@app.get("/stand1")
async def stand1(user_id: int): #async
    await asyncio.sleep(0.1) # Тяжелый запрос в Postgres (Стенд 1)
    cur = db.cursor()
    cur.execute("""
		SELECT i.name FROM items i 
		JOIN events e ON i.item_id = e.item_id 
		WHERE e.user_id = %s 
		GROUP BY i.name 
		ORDER BY count(e.event_id) DESC 
		LIMIT 10
	""", (user_id,))
    res = cur.fetchall()
    cur.close()
    return res

@app.get("/stand2")
def stand2(user_id: int):
    # Легкий запрос: берем категорию из Redis, а товар из Postgres (Стенд 2)
    cat = r.get(f"user:{user_id}:fav") or "Электроника"
    cur = db.cursor()
    cur.execute("SELECT name FROM items WHERE category = %s LIMIT 5", (cat,))
    res = cur.fetchall()
    cur.close()
    return res