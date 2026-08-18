from pymongo import MongoClient #type: ignore
import os
from dotenv import load_dotenv #type: ignore

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URI"))

db = client["mydatabase"]
user_collection = db["users"]

