# Transaction Webhook Service

FastAPI + MongoDB + Celery + Redis

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Fill in your MongoDB URI and Redis URL in .env
```

## Run

**Terminal 1 — FastAPI server:**
```bash
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — Celery worker:**
```bash
celery -A app.worker.celery_app worker --loglevel=info
```

## Test

**Health check:**
```bash
curl http://localhost:8000/
```

**Send a webhook:**
```bash
curl -X POST http://localhost:8000/v1/webhooks/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "txn_abc123",
    "source_account": "acc_user_789",
    "destination_account": "acc_merchant_456",
    "amount": 1500,
    "currency": "INR"
  }'
```

**Check transaction status (after ~30s):**
```bash
curl http://localhost:8000/v1/transactions/txn_abc123
```

**Test idempotency (send same webhook multiple times):**
```bash
for i in {1..5}; do
  curl -X POST http://localhost:8000/v1/webhooks/transactions \
    -H "Content-Type: application/json" \
    -d '{"transaction_id":"txn_abc123","source_account":"acc_user_789","destination_account":"acc_merchant_456","amount":1500,"currency":"INR"}'
done
```
Only one transaction should exist in MongoDB.

## Architecture

```
Webhook → FastAPI (202 immediately)
              ↓
         MongoDB insert (unique index = idempotency layer 1)
              ↓
         Celery task queued via Redis
              ↓
         Worker picks up task
              ↓
         Check MongoDB status (idempotency layer 2)
              ↓
         30s simulated processing
              ↓
         MongoDB updated → status: PROCESSED
```
