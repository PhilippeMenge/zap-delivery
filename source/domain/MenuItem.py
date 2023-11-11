from dataclasses import dataclass


@dataclass
class MenuItem:
    """### Represents an item in the menu."""

    id: str
    name: str
    price: str
    description: str
    is_active: bool
