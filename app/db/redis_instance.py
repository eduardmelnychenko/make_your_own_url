import redis
from app.creds.settings import CacheSettings

redis_client = redis.Redis(host=CacheSettings.REDIS_HOST,
                           port=CacheSettings.REDIS_PORT,
                           password=CacheSettings.REDIS_PASS)

