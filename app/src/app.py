from fastapi import FastAPI
from src.routers import stripe_webhook_router, whatsapp_webhook_router

api = FastAPI()

api.include_router(whatsapp_webhook_router.router, prefix="/whatsapp")
api.include_router(stripe_webhook_router.router, prefix="/stripe")
