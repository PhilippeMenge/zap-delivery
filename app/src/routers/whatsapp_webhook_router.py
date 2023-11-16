import logging

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

router = APIRouter()


@router.get("/")
def verify_token(request: Request):
    """### Webhook endpoint for WhatsApp verification."""
    if request.query_params.get("hub.verify_token") == WHATSAPP_VERIFY_TOKEN:
        logging.info("Verified webhook")
        challenge = request.query_params.get("hub.challenge")
        return Response(content=challenge, media_type="text/plain", status_code=200)
    logging.error("Webhook Verification failed")
    return Response(
        content="Verification failed", media_type="text/plain", status_code=403
    )


@router.post("/")
async def handle_webhook(request: Request):
    """### Webhook endpoint for handling events."""
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

    OPENAI_INTEGRATION_SERVICE.send_user_message(thread_id, message)
    OPENAI_INTEGRATION_SERVICE.request_run_assistant_on_thread(thread_id)
    return Response(status_code=200)


@router.get("/execute_due_requests")
async def execute_due_requests():
    messages = OPENAI_INTEGRATION_SERVICE.execute_due_requests()

    for thread_id, message in messages.items():
        phone_number = USER_THREAD_REPOSITORY.get_phone_number_from_thread_id(thread_id)
        if phone_number is None:
            logging.error(
                f"Thread ID {thread_id} does not have a phone number associated"
            )
            continue

        WHATSAPP_INTEGRATION_SERVICE.send_message(message, phone_number)

    return Response(status_code=200)
