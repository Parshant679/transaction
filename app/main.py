from contextlib import asynccontextmanager
from fastapi import FastAPI
from datetime import datetime, timezone

from app.database import connect_db, close_db
from app.models import HealthResponse
from app.router.webhook import router as webhook_router

app = FastAPI(
    title="Transaction Webhook Service",
    description="Receives payment processor webhooks and processes transactions reliably in the background.",
    version="1.0.0",
)
# server lifecycle events 
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    await connect_db()
    yield
    # --- Shutdown ---
    await close_db()

@app.get("/", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="HEALTHY",
        current_time=datetime.now(timezone.utc),
    )

# Routers

app.include_router(webhook_router, prefix="/v1")