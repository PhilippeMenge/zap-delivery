from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import Response
from src.routers.common import ORDER_SERVICE, STRIPE_INTEGRATION_SERVICE
from src.utils.logging import get_configured_logger

logger = get_configured_logger(__name__)

router = APIRouter()


@router.post("/checkout")
async def checkout(request: Request):
    """### Webhook endpoint for Stripe checkout session events."""
    logger.debug("Received Stripe Checkout Session webhook event.")
    payload = await request.json()

    (
        checkout_session_id,
        is_successful,
    ) = STRIPE_INTEGRATION_SERVICE.get_payment_session_event_info(payload)

    ORDER_SERVICE.process_order_payment(checkout_session_id, is_successful)

    logger.debug("Processed Stripe Checkout Session webhook event.")
    return Response(status_code=200)
