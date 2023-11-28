from dataclasses import dataclass
from src.domain.Establishment import Establishment

@dataclass
class SafeMenuItem:
    """### Represents an item in the menu."""

    id: str
    name: str
    price: str
    description: str
    is_active: bool
@dataclass
class MenuItem:
    """### Represents an item in the menu."""

    id: str
    name: str
    price: str
    description: str
    is_active: bool
    establishment: Establishment

    def to_safe(self) -> SafeMenuItem:
        """### Returns a safe version of the menu item."""
        return SafeMenuItem(
            id=self.id,
            name=self.name,
            price=self.price,
            description=self.description,
            is_active=self.is_active
        )
