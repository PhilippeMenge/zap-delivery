import stripe
from src.config import STRIPE_API_KEY
from src.domain.Order import Order
from src.domain.OrderItem import OrderItem
from src.utils.logging import get_configured_logger

logger = get_configured_logger(__name__)


class StripeIntegrationService:
    def __init__(self):
        stripe.api_key = STRIPE_API_KEY

    def create_checkout_session(self, order: Order) -> tuple[str, str]:
        """### Create a checkout session in Stripe

        Args:
            order (Order): The order to be paid

        Returns:
            tuple[str, str]: (session_id, session_url)
        """

        def build_line_item(item: OrderItem):
            return {
                "price_data": {
                    "currency": "brl",
                    "product_data": {
                        "name": item.menu_item.name,
                    },
                    "unit_amount_decimal": float(item.menu_item.price) * 100,
                },
                "quantity": item.amount,
            }

        session = stripe.checkout.Session.create(
            line_items=[build_line_item(item) for item in order.itens],
            mode="payment",
            success_url="https://www.google.com",
            cancel_url="https://www.google.com",
        )

        if session.url is None:
            raise Exception("Failed to create checkout session. Session URL is None.")

        logger.info(f"Created checkout session {session.id}")
        return session.id, session.url

    def get_payment_session_event_info(self, payload) -> tuple[str, bool]:
        """### Get payment session event info from Stripe

        Args:
            payload (str): The payload from the webhook

        Returns:
            tuple[str, bool]: (session_id, success)
        """

        event = stripe.Event.construct_from(payload, STRIPE_API_KEY)

        session = event["data"]["object"]

        if event["type"] == "checkout.session.completed":
            logger.info(f"Checkout session {session['id']} completed.")
            return session["id"], True

        logger.info(f"Checkout session {session['id']} failed.")
        return session["id"], False
