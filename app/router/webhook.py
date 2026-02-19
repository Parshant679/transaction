from fastapi import APIRouter , HTTPException ,status
from app.models import TransactionRequest,TransactionResponse,WebhookAckResponse
from app.database import get_collection
from app.worker import process_transaction_task
from datetime import datetime,timezone
from pymongo.errors import DuplicateKeyError

router = APIRouter()
@router.post(
    "/webhooks/transactions",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=WebhookAckResponse,
)
async def receive_transaction_webhook(payload: TransactionRequest):
    collection = get_collection("transactions")
    transaction_doc = {
        "transaction_id": payload.transaction_id,
        "source_account": payload.source_account,
        "destination_account": payload.destination_account,
        "amount": payload.amount,
        "currency": payload.currency,
        "status": "PROCESSING",
        "created_at": datetime.now(timezone.utc),
        "processed_at": None,
    }

    try:
        await collection.insert_one(transaction_doc)
        process_transaction_task.delay(transaction_doc)
        print(f"Queued task for transaction {payload.transaction_id}")

    except DuplicateKeyError:
        print(f" Duplicate webhook received for {payload.transaction_id}. Ignoring.")

    return WebhookAckResponse(
        message="Webhook received",
        transaction_id=payload.transaction_id,
    )


@router.get(
    "/transactions/{transaction_id}",
    response_model=list[TransactionResponse],
)
async def get_transaction(transaction_id: str):

    collection = get_collection("transactions")
    doc = await collection.find_one(
        {"transaction_id": transaction_id},
        {"_id": 0}, 
    )

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction {transaction_id} not found",
        )

    return [TransactionResponse(**doc)]