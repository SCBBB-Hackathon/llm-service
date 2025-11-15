import redis_client
from loguru import logger

class RedisClient:
    def __init__(self, config):
        self.client = redis_client.Redis(
            host=config["host"],
            port=config["port"],
            db=config["db"],
            decode_responses=True
        )
        logger.info("Redis connected")

    def set_data(self, key, value):
        self.client.set(key, value)

    def get_data(self, key):
        return self.client.get(key)
