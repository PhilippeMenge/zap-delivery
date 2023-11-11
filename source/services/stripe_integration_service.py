import json

import stripe
from config import STRIPE_API_KEY, STRIPE_ENDPOINT_SECRET
from domain import Order
from domain.OrderItem import OrderItem


class StripeIntegrationService:
    def __init__(self):
        stripe.api_key = STRIPE_API_KEY

    def create_checkout_session(self, order: Order) -> tuple[str, str] | None:
        """### Create a checkout session in Stripe

        Args:
            order (Order): The order to be paid

        Returns:
            tuple[str, str]: (session_id, session_url) if successful. None if not.
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

        try:
            session = stripe.checkout.Session.create(
                line_items=[build_line_item(item) for item in order.itens],
                mode="payment",
                success_url="https://www.google.com",
                cancel_url="https://www.google.com",
            )

            return session.id, session.url  # type: ignore
        except Exception as e:
            print(e)
            return None

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
            return session["id"], True

        return session["id"], False
        