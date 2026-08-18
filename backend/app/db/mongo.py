"""MongoDB connection management."""
from pymongo import MongoClient
from pymongo.database import Database

from app.core.config import settings
from app.core.logging import logger


class MongoDB:
    """MongoDB connection wrapper."""

    client: MongoClient = None
    db: Database = None


mongo = MongoDB()


def connect_to_mongo() -> None:
    """Establish MongoDB connection on startup."""
    try:
        mongo.client = MongoClient(settings.MONGO_URL, serverSelectionTimeoutMS=5000)
        mongo.db = mongo.client[settings.MONGO_DB]
        # Force connection to verify
        mongo.client.admin.command("ping")
        logger.info("Connected to MongoDB successfully")
    except Exception as e:
        logger.warning(f"MongoDB connection failed (will run in degraded mode): {e}")


def close_mongo_connection() -> None:
    """Close MongoDB connection on shutdown."""
    if mongo.client:
        mongo.client.close()
        logger.info("MongoDB connection closed")


def get_mongo_db() -> Database:
    """Return the MongoDB database instance."""
    return mongo.db
