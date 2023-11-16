from dataclasses import dataclass

from src.domain.MenuItem import MenuItem


@dataclass
class OrderItem:
    """### Represents an item in an order."""

    menu_item: MenuItem
    amount: int
    observation: str
    order_id: str | None = None
