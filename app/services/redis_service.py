import json
import logging
from typing import Any

import redis
from redis import RedisError

from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisService:
    _memory_store: dict[int, list[dict[str, Any]]] = {}

    def __init__(self):
        self.redis_client = None
        try:
            client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            client.ping()
            self.redis_client = client
        except RedisError:
            logger.warning("Redis unavailable, using in-memory conversation store.")
        except Exception:
            logger.warning("Redis unavailable, using in-memory conversation store.")

    def set_cache(self, key: str, value: str, ttl: int = 3600):
        if self.redis_client is not None:
            self.redis_client.setex(key, ttl, value)

    def get_cache(self, key: str) -> str:
        if self.redis_client is None:
            return ""
        return self.redis_client.get(key) or ""

    def get_conversation_history(self, user_id: int) -> list[dict[str, Any]]:
        key = f"conversation:{user_id}"
        if self.redis_client is None:
            return list(self._memory_store.get(user_id, []))
        data = self.redis_client.get(key)
        return json.loads(data) if data else []

    def save_conversation_history(
        self,
        user_id: int,
        history: list[dict[str, Any]],
        ttl: int = 86400,
    ):
        key = f"conversation:{user_id}"
        trimmed_history = history[-50:]
        if self.redis_client is None:
            self._memory_store[user_id] = list(trimmed_history)
            return
        self.redis_client.setex(key, ttl, json.dumps(trimmed_history))

    def add_message_to_history(self, user_id: int, message: dict[str, Any]):
        history = self.get_conversation_history(user_id)
        history.append(message)
        self.save_conversation_history(user_id, history)

    def clear_conversation_history(self, user_id: int):
        key = f"conversation:{user_id}"
        if self.redis_client is None:
            self._memory_store.pop(user_id, None)
            return
        self.redis_client.delete(key)
