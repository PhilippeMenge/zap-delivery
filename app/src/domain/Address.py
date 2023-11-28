from __future__ import annotations
import uuid
from dataclasses import dataclass, field


@dataclass
class Address:
    """### Represents an address."""

    street: str
    number: str
    complement: str | None
    neighborhood: str
    city: str
    state: str
    country: str
    zipcode: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __str__(self):
        return f"{self.street}, {self.number} - {self.complement} - {self.neighborhood} - {self.city} - {self.state} - {self.country}"

    def to_safe(self) -> Address:
        """### Returns a safe version of the address."""
        return self




        