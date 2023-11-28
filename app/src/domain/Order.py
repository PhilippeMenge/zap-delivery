import uuid
from dataclasses import dataclass, field
from enum import Enum

from src.domain.Address import Address
from src.domain.OrderItem import OrderItem

from src.domain.User import User


class OrderStatus(Enum):
    AWAITING_PAYMENT = "AWAITING_PAYMENT"
    IN_PREPARATION = "IN_PREPARATION"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    CONTACT_SUPPORT = "CONTACT_SUPPORT"



@dataclass
class SafeOrder:
    """### Represents an order."""

    address: Address
    status: OrderStatus
    itens: list[OrderItem]
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
@dataclass
class Order:
    """### Represents an order."""

    address: Address
    status: OrderStatus
    itens: list[OrderItem]
    user: User
    checkout_session_id: str | None = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_safe(self) -> SafeOrder:
        """### Returns a safe version of the order."""
        return SafeOrder(
            address=self.address,
            status=self.status,
            itens=self.itens,
            id=self.id
        )