from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load .env explicitly
load_dotenv()

uri = os.getenv("MONGODB_URL")
print(f"Testing connection with URI: {uri}")

try:
    client = MongoClient(uri)
    # The ismaster command is cheap and does not require auth.
    # The ping command requires auth.
    client.admin.command('ping')
    print("SUCCESS: Connected to MongoDB Atlas!")
except Exception as e:
    print(f"FAILED: {e}")
