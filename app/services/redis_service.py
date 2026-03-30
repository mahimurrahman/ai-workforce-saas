import redis
from app.core.config import settings

class RedisService:
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL)

    def set_cache(self, key: str, value: str, ttl: int = 3600):
        self.redis_client.setex(key, ttl, value)

    def get_cache(self, key: str) -> str:
        return self.redis_client.get(key)

    # Add more methods as needed