from fastapi import FastAPI
from src.routers import cronjobs_router, stripe_webhook_router, whatsapp_webhook_router, webapp_router, auth_router
from src.utils.logging import get_configured_logger

logger = get_configured_logger(__name__)

api = FastAPI()

api.include_router(whatsapp_webhook_router.router, prefix="/whatsapp")
api.include_router(stripe_webhook_router.router, prefix="/stripe")
api.include_router(cronjobs_router.router, prefix="/cronjobs")
api.include_router(webapp_router.router, prefix="/webapp")
api.include_router(auth_router.router, prefix="/auth")


@api.get("/")
def root():
    logger.debug("Root endpoint called.")
    return {"message": "Hello World"}


logger.info("API started.")
