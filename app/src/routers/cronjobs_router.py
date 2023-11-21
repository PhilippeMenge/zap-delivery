from fastapi import APIRouter
from fastapi.responses import Response
from src.routers.common import (
    OPENAI_INTEGRATION_SERVICE,
    USER_REPOSITORY,
    WHATSAPP_INTEGRATION_SERVICE,
)
from src.utils.logging import get_configured_logger

logger = get_configured_logger(__name__)

router = APIRouter()


@router.get("/execute_due_requests")
async def execute_due_requests():
    """### Execute all due run_assistant requests."""
    logger.debug("Received execute due requests request.")

    messages_per_thread = (
        OPENAI_INTEGRATION_SERVICE.execute_due_run_assistant_requests()
    )

    for thread_id, messages in messages_per_thread.items():
        user = USER_REPOSITORY.get_user_from_thread_id(thread_id)
        if user is None:
            logger.error(f"Thread ID {thread_id} does not have a user associated.")
            continue

        phone_number = user.phone_number
        establishment = user.establishment
        if phone_number is None:
            logger.error(
                f"Thread ID {thread_id} does not have a phone number associated."
            )
            continue

        for message in messages:
            WHATSAPP_INTEGRATION_SERVICE.send_message(
                message, phone_number, establishment
            )

    logger.debug("Processed execute due requests request.")
    return Response(status_code=200)
