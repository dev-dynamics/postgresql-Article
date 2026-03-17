from locust import HttpUser, task, between
import random

class LoadTester(HttpUser):
    wait_time = between(1, 5)

    @task
    def test_logic(self):
        uid = random.randint(1, 100000)
        # Для Стенда 1:
        self.client.get(f"/stand1?user_id={uid}", name="Stand 1: Postgres")
        # Для Стенда 2 (раскомментируй потом):
        #self.client.get(f"/stand2?user_id={uid}", name="Stand 2: Hybrid")