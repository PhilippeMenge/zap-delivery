from domain.Order import OrderStatus
from fastapi import APIRouter, Header
from fastapi.requests import Request
from routers.common import (
    ORDER_REPOSITORY,
    STRIPE_INTEGRATION_SERVICE,
    WHATSAPP_INTEGRATION_SERVICE,
)

router = APIRouter()


@router.post("/checkout")
async def checkout(request: Request):
    """### Webhook endpoint for Stripe checkout session events."""
    payload = await request.json()

    event_info = STRIPE_INTEGRATION_SERVICE.get_payment_session_event_info(payload)
    order = ORDER_REPOSITORY.get_order_by_checkout_session_id(event_info[0])

    if order is None:
        return "Order not found", 404

    order.status = OrderStatus.CONFIRMED
    ORDER_REPOSITORY.add_order(order)

    phone_number = order.user_thread.phone_number
    WHATSAPP_INTEGRATION_SERVICE.send_message(
        "Seu pedido foi confirmado! Em breve você receberá atualizações sobre o status do seu pedido.",
        phone_number,
    )
