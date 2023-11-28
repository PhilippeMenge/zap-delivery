from dataclasses import dataclass

from src.domain.MenuItem import MenuItem
from src.domain.Establishment import Establishment


@dataclass
class OrderItem:
    """### Represents an item in an order."""

    menu_item: MenuItem
    amount: int
    observation: str
    establishment: Establishment
    order_id: str | None = None
