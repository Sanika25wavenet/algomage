from motor.motor_asyncio import AsyncIOMotorClient
from .settings import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None

    async def connect(self):
        """Establishes a connection to the MongoDB database."""
        try:
            self.client = AsyncIOMotorClient(settings.MONGODB_URL)
            # Verify connection
            await self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB Atlas!")
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {e}")
            raise e

    def close(self):
        """Closes the MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed.")

    def get_db(self):
        """Returns the database instance."""
        if self.client:
            return self.client[settings.DATABASE_NAME]
        raise ConnectionError("Database not initialized. Call connect() first.")

db = Database()
