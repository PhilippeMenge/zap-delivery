import uuid
from dataclasses import dataclass, field

from src.domain.Address import Address


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
