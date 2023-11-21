from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import Response
from src.config import WHATSAPP_VERIFY_TOKEN
from src.domain.User import User
from src.routers.common import (
    ESTABLISHMENT_REPOSITORY,
    OPENAI_INTEGRATION_SERVICE,
    USER_REPOSITORY,
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

    whatsapp_phone_number_id = data["entry"][0]["changes"][0]["value"]["metadata"][
        "phone_number_id"
    ]
    establishment = (
        ESTABLISHMENT_REPOSITORY.get_establishment_from_whatsapp_phone_number_id(
            whatsapp_phone_number_id
        )
    )

    if establishment is None:
        logger.error(
            f"Received WhatsApp webhook event for unknown WhatsApp phone number ID {whatsapp_phone_number_id}."
        )
        return Response(status_code=400)

    message_data = WHATSAPP_INTEGRATION_SERVICE.get_message_text(data, establishment)

    if message_data is None:
        return Response(status_code=200)

    message, mobile = message_data

    user = USER_REPOSITORY.get_user_from_phone_number(mobile, establishment)
    if user is None:
        thread_id = OPENAI_INTEGRATION_SERVICE.create_thread()

        user = User(
            phone_number=mobile, thread_id=thread_id, establishment=establishment
        )

        USER_REPOSITORY.create_user(user)

    thread_id = user.thread_id

    OPENAI_INTEGRATION_SERVICE.add_user_message_to_thread(thread_id, message)
    OPENAI_INTEGRATION_SERVICE.request_run_assistant_on_thread(thread_id)

    logger.info("Processed WhatsApp webhook event.")
    return Response(status_code=200)
