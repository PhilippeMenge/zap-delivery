from dataclasses import dataclass


@dataclass
class MenuItem:
    id: str
    name: str
    price: str
    description: str
    is_active: bool
