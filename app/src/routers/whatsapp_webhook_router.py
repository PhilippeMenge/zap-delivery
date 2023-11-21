from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import Response
from src.config import WHATSAPP_VERIFY_TOKEN
from src.domain.UserThread import UserThread
from src.routers.common import (
    OPENAI_INTEGRATION_SERVICE,
    USER_THREAD_REPOSITORY,
    WHATSAPP_INTEGRATION_SERVICE,
)
from src.utils.logging import get_configured_logger

logger = get_configured_logger(__name__)

router = APIRouter()


@router.get("/")
def verify_token(request: Request):
    """### Webhook endpoint for WhatsApp verification."""
    logger.info("Received WhatsApp webhook verification request.")

    if request.query_params.get("hub.verify_token") == WHATSAPP_VERIFY_TOKEN:
        logger.info("Verified webhook")
        challenge = request.query_params.get("hub.challenge")

        logger.info("WhatsApp webhook verification request processed.")
        return Response(content=challenge, media_type="text/plain", status_code=200)

    logger.critical(
        "WhatsApp webhook verification request failed. This could prevent WhatsApp messages from being processed."
    )
    return Response(
        content="Verification failed", media_type="text/plain", status_code=403
    )


@router.post("/")
async def handle_webhook(request: Request):
    """### Webhook endpoint for handling events."""
    logger.info("Received WhatsApp webhook event.")
    data = await request.json()
    message_data = WHATSAPP_INTEGRATION_SERVICE.get_message_text(data)

    if message_data is None:
        return Response(status_code=200)

    message, mobile = message_data

    user_thread = USER_THREAD_REPOSITORY.get_user_thread_from_phone_number(mobile)
    if user_thread is None:
        thread_id = OPENAI_INTEGRATION_SERVICE.create_thread()

        user_thread = UserThread(phone_number=mobile, thread_id=thread_id)

        USER_THREAD_REPOSITORY.create_user_thread(user_thread)

    thread_id = user_thread.thread_id

    OPENAI_INTEGRATION_SERVICE.add_user_message_to_thread(thread_id, message)
    OPENAI_INTEGRATION_SERVICE.request_run_assistant_on_thread(thread_id)

    logger.info("Processed WhatsApp webhook event.")
    return Response(status_code=200)
