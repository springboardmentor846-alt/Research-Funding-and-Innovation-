import logging
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

logger = logging.getLogger(__name__)

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

db_mongo = MongoDB()

async def connect_to_mongo():
    try:
        db_mongo.client = AsyncIOMotorClient(settings.MONGODB_URL, serverSelectionTimeoutMS=2000)
        db_mongo.db = db_mongo.client[settings.MONGODB_DB_NAME]
        logger.info("Connected to MongoDB document store.")
    except Exception as e:
        logger.warning(f"MongoDB connection deferred/unavailable: {e}")

async def close_mongo_connection():
    if db_mongo.client:
        db_mongo.client.close()
        logger.info("MongoDB connection closed.")

def get_mongo_db():
    return db_mongo.db
