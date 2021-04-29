import redis

redis_client = redis.Redis(host='cache', port=6379, password='rcmnd-pass')
