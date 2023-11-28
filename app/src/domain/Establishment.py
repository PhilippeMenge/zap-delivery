import uuid
from dataclasses import dataclass, field

from src.domain.Address import Address


@dataclass
class SafeEstablishment:
    """### Represents an establishmemt."""

    name: str
    address: Address
    contact_number: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass
class Establishment:
    """### Represents an establishmemt."""

    name: str
    estimated_production_minutes: int
    address: Address
    custom_prompt_section: str
    whatsapp_api_key: str
    whatsapp_number_id: str
    contact_number: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_safe(self) -> SafeEstablishment:
        """### Returns a safe version of the establishment."""
        return SafeEstablishment(
            name=self.name,
            address=self.address.to_safe(),
            contact_number=self.contact_number,
            id=self.id
        )