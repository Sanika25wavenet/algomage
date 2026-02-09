import asyncio
from config.database import db

async def verify_connection():
    try:
        print("Attempting to connect to MongoDB...")
        await db.connect()
        print("Connection successful!")
        db.close()
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(verify_connection())
    except ImportError as e:
        print(f"ImportError: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
