from dataclasses import dataclass

from domain import MenuItem


@dataclass
class OrderItem:
    """### Represents an item in an order."""
    menu_item: MenuItem
    amount: int
    observation: str
    order_id: str | None = None
