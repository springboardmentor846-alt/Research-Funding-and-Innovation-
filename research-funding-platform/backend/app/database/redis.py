import logging
import redis
from app.core.config import settings

logger = logging.getLogger(__name__)

class RedisClient:
    def __init__(self):
        try:
            self.client = redis.from_url(settings.REDIS_URL, decode_responses=True, socket_timeout=1)
        except Exception as e:
            logger.warning(f"Redis client initialization error: {e}")
            self.client = None

    def get(self, key: str):
        if not self.client:
            return None
        try:
            return self.client.get(key)
        except Exception:
            return None

    def set(self, key: str, value: str, ex: int = 3600):
        if not self.client:
            return False
        try:
            return self.client.set(key, value, ex=ex)
        except Exception:
            return False

redis_client = RedisClient()
