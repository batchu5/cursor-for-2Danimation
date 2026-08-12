from pymongo import MongoClient #type: ignore

client = MongoClient("mongodb+srv://admin:M8Ka9GxEjWaNb9kl@cluster0.lphgo.mongodb.net/")

db = client["mydatabase"]
user_collection = db["users"]
