# Сравнительный анализ производительности: PostgreSQL vs Hybrid (PostgreSQL + Redis)

Данный проект представляет собой стенд для нагрузочного тестирования двух архитектурных подходов к хранению и выборке данных в высоконагруженных системах. 

## 🚀 Стек технологий
* **Backend:** FastAPI (Python 3.13)
* **Database:** PostgreSQL 16
* **Caching:** Redis
* **Load Testing:** Locust
* **Environment:** Linux (Ubuntu / WSL2) — *рекомендуется для тестов 1000+ RPS*

---

## 🛠 Требования и установка

### 🐧 Linux (Рекомендуется) / WSL2
Использование Linux критично для обхода ограничений системного вызова `select()` в Windows, что позволяет обрабатывать >1024 одновременных соединений через `epoll`.

#### 1. Системные зависимости
```bash
sudo apt update
sudo apt install postgresql redis-server python3-pip
```

2. Настройка базы данных
Bash
# Вход в Postgres
```sudo -u postgres psql
```

# Выполнение SQL команд
```sql
CREATE DATABASE kino;
CREATE USER postgres WITH PASSWORD 'root';
ALTER ROLE postgres WITH SUPERUSER;
```


3. Настройка прав доступа (pg_hba.conf)
Для корректной работы пула соединений в pg_hba.conf установите метод md5 или trust для локальных подключений:
host all all 127.0.0.1/32 trust


4. Запуск приложения
```Bash
pip install -r requirements.txt
python3 app.py
```


🪟 Windows (Для разработки)
Примечание: При нагрузке свыше 500-1000 пользователей возможны ошибки ValueError: too many file descriptors.

Установите PostgreSQL и Redis for Windows.

Установите зависимости: ```pip install -r requirements.txt```

Убедитесь, что в коде включен фикс для Windows:

```Python
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
```

📊 Методология тестирования
Тестирование проводилось с помощью Locust при следующих параметрах:

Количество пользователей: 1000

Spawn Rate: 10 юзеров/сек

Интервал запросов: 1-2 сек

Сценарии:
Stand 1 (Postgres): Тяжелый SQL-запрос с JOIN, GROUP BY и ORDER BY по таблице на 100,000 записей.

Stand 2 (Hybrid): Выборка предоптимизированных данных из кэша Redis + легкий запрос в Postgres по индексу.


<img width="756" height="322" alt="image" src="https://github.com/user-attachments/assets/cef6868b-d50b-48c6-8e91-5a24d8eb1fa8" />
