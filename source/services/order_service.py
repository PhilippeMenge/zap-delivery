from domain.Order import Order, OrderStatus
from infrastructure.repositories.order_repository import OrderRepository
from services.stripe_integration_service import StripeIntegrationService
from services.whatsapp_integration_service import WhatsappIntegrationService


class OrderService:
    def __init__(
        self,
        orderRepository: OrderRepository,
        stripeIntegrationService: StripeIntegrationService,
        whatsappIntegrationService: WhatsappIntegrationService,
    ):
        self._orderRepository = orderRepository
        self._stripeIntegrationService = stripeIntegrationService
        self._whatsappIntegrationService = whatsappIntegrationService

    def get_order(self, order_id: str) -> Order | None:
        """### Get an order from its id.

        Args:
            order_id (str): The id of the order.

        Returns:
            Order: The order instance. None if not found.
        """
        return self._orderRepository.get_order(order_id)

    def create_order(self, order: Order) -> str:
        """### Create an order and an associated checkout session.

        Args:
            order (Order): The order to create.

        Returns:
            str: The checkout session URL.
        """
        checkout_session_data = self._stripeIntegrationService.create_checkout_session(
            order
        )

        if checkout_session_data is None:
            raise Exception("Failed to create checkout session.")

        order.checkout_session_id, checkout_session_url = checkout_session_data

        self._orderRepository.add_order(order)
        return checkout_session_url

    def update_order_status(self, order_id: str, order_status: OrderStatus):
        """### Update an order status.

        Args:
            order_id (str): The id of the order.
            order_status (OrderStatus): The new status of the order.
        """
        order = self._orderRepository.get_order(order_id)
        if order is None:
            raise Exception("Order not found.")
        order.status = order_status
        self._orderRepository.add_order(order)

    def process_order_payment(self, checkout_session_id: str, is_successful: bool):
        """### Process the payment of an order.

        Args:
            checkout_session_id (str): The checkout session id.
        """
        order = self._orderRepository.get_order_by_checkout_session_id(
            checkout_session_id
        )
        if order is None:
            raise Exception("Order not found.")

        if is_successful:
            self.update_order_status(order.id, OrderStatus.IN_PREPARATION)
            self._whatsappIntegrationService.send_message(
                f"Seu pedido foi pago com sucesso e está sendo preparado.",
                order.user_thread.phone_number,
            )
        else:
            self.update_order_status(order.id, OrderStatus.CANCELLED)
            self._whatsappIntegrationService.send_message(
                f"Seu pedido foi cancelado. Entre em contato conosco para mais informações.",
                order.user_thread.phone_number,
            )
