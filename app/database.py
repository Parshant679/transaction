from pymongo import AsyncMongoClient
from pymongo.asynchronous.collection import AsyncCollection
import os
from dotenv import load_dotenv
load_dotenv()

class Settings:
    def __init__(self):
       self.mongo_uri  = os.getenv("MONGO_URI")
       self.db_name  = os.getenv("DB_NAME")
       self.redis_url  = os.getenv("REDIS_URL")
       print(self.mongo_uri,self.db_name,self.redis_url)

settings = Settings()

class Database:
    def __init__(self):
     self.client : AsyncMongoClient  = None

db = Database()

async def connect_db():
    db.client =  AsyncMongoClient(
        settings.mongo_uri,
        maxPoolSize=10,
        minPoolSize=2
    )
    collection = db.client[settings.db_name]["transactions"]
    await collection.create_index("transaction_id",unique=True)

async def close_db():
    if db.client:
        await db.client.close()

def get_collection(name: str):
    collection = db.client[settings.db_name][name]
    return collection