from django.core.management.base import BaseCommand
import redis
import time

class Command(BaseCommand):
    def handle(self, *args, **options):
        r = redis.Redis(host='redis', port=6379, db=0)
        attempts = 0
        while True:
            try:
                if r.ping():
                    self.stdout.write("✅ Redis connection established")
                    break
            except redis.ConnectionError:
                attempts += 1
                if attempts > 30:
                    raise RuntimeError("Failed to connect to Redis after 30 attempts")
                self.stdout.write(f"⏳ Waiting for Redis... ({attempts}/30)")
                time.sleep(1)