from src.domain.Order import Order
from src.infrastructure.models.OrderModel import OrderModel
from sqlalchemy.orm import Session


class OrderRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_order(self, order_id: str) -> Order | None:
        """### Get an order from its id.

        Args:
            order_id (str): The id of the order.

        Returns:
            Order: The order instance. None if not found.
        """
        order_model = self.session.query(OrderModel).get(order_id)
        if order_model is None:
            return None
        return order_model.to_entity()

    def add_order(self, order: Order):
        """### Add an order.

        Args:
            order (Order): The order to add.
        """
        order_model = OrderModel.from_entity(order)
        self.session.merge(order_model)
        self.session.commit()

    def get_order_by_checkout_session_id(
        self, checkout_session_id: str
    ) -> Order | None:
        """### Get an order from its checkout session id.

        Args:
            checkout_session_id (str): The checkout session id of the order.

        Returns:
            Order: The order instance. None if not found.
        """
        order_model = (
            self.session.query(OrderModel)
            .filter_by(checkout_session_id=checkout_session_id)
            .first()
        )
        if order_model is None:
            return None
        return order_model.to_entity()