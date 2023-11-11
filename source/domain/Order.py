import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum

from domain.OrderItem import OrderItem
from domain.UserThread import UserThread


class OrderStatus(Enum):
    AWAITING_PAYMENT = "AWAITING_PAYMENT"
    IN_PREPARATION = "IN_PREPARATION"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    CANCELED = "CANCELED"
    CONTACT_SUPPORT = "CONTACT_SUPPORT"


@dataclass
class Order:
    """### Represents an order."""

    address: str
    status: OrderStatus
    itens: list[OrderItem]
    user_thread: UserThread
    checkout_session_id: str | None = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __dict__(self):
        return {
            "address": self.address,
            "status": self.status.value,
            "itens": [asdict(item) for item in self.itens],
            "id": self.id,
        }
