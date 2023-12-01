from dataclasses import dataclass

from src.domain.Establishment import Establishment
from src.domain.MenuItem import MenuItem, SafeMenuItem


@dataclass
class SafeOrderItem:
    """### Represents an item in an order."""

    menu_item: SafeMenuItem
    amount: int
    observation: str
    order_id: str | None = None


@dataclass
class OrderItem:
    """### Represents an item in an order."""

    menu_item: MenuItem
    amount: int
    observation: str
    establishment: Establishment
    order_id: str | None = None

    def to_safe(self) -> SafeOrderItem:
        """### Returns a safe version of the order item."""
        return SafeOrderItem(
            menu_item=self.menu_item.to_safe(),
            amount=self.amount,
            observation=self.observation,
            order_id=self.order_id,
        )
