from pymongo import AsyncMongoClient
from pymongo.asynchronous.collection import AsyncCollection
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongo_uri:str
    db_name : str = "webhook"
    redis_url : str
    class Config:
        env_file = ".env"

settings = Settings()

class Database:
    client : AsyncMongoClient  = None

db = Database()

async def connect_db():
    db.client =  AsyncMongoClient(
        settings.mongo_uri,
        maxPoolSize=10,
        minPoolSize=2
    )
    
    collection = db.client[settings.db_name]["transactions"]
    await collection.create_index("transaction_id",unique=True)

async def close_db_connection():
    if db.client:
        await db.client.close()

def get_collection(name: str):
    return db.client[settings.db_name][name]