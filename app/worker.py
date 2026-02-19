import time
from celery import Celery
from celery.signals import worker_process_init, worker_process_shutdown
from pymongo import MongoClient
from datetime import datetime, timezone
from app.database import settings


celery_app = Celery(
    "webhook_worker",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

mongo_client = None
transactions_collection = None


mongo_client = MongoClient(
        settings.mongo_uri,
        maxPoolSize=10,  
        minPoolSize=2,   
    )
transactions_collection = mongo_client[settings.db_name]["transactions"]
 

@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)
def process_transaction_task(self, transaction_id:str):
    
    try:
        existing = transactions_collection.find_one({"transaction_id": transaction_id})

        if not existing:
            print("transaction {transaction_id} not found in DB. Invalid transaction")
            return

        if existing["status"] == "PROCESSED":
            print("transaction {transaction_id} already processed")
            return

        # simulating external api call
        time.sleep(30)

        # update teansaction status to PROCESSED
        transactions_collection.update_one(
            {"transaction_id": transaction_id},
            {
                "$set": {
                    "status": "PROCESSED",
                    "processed_at": datetime.now(timezone.utc),
                }
            },
        )
        print("transaction {transaction_id} marked as PROCESSED.")

    except Exception as exc:
        print("error processing {transaction_id}: {exc}")
        raise self.retry(exc=exc)
