from dataclasses import dataclass
from src.domain.Establishment import Establishment


@dataclass
class MenuItem:
    """### Represents an item in the menu."""

    id: str
    name: str
    price: str
    description: str
    is_active: bool
    establishment: Establishment
