from motor.motor_asyncio import AsyncIOMotorClient
from utils.getAPI import getApiKey

MONGO_URL = getApiKey("MONGO_URL")

def create_mongo_client():
    client = AsyncIOMotorClient(
        MONGO_URL,
        maxPoolSize=10,
        minPoolSize=1,
    )
    return client