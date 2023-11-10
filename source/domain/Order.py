import uuid
from dataclasses import dataclass, field
from enum import Enum

from domain.OrderItem import OrderItem


class OrderStatus(Enum):
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    PREPARING = "PREPARING"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"


@dataclass
class Order:
    address: str
    status: OrderStatus
    itens: list[OrderItem]
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __dict__(self):
        return {
            "address": self.address,
            "status": self.status.value,
            "itens": [item.__dict__() for item in self.itens],
            "id": self.id,
        }
