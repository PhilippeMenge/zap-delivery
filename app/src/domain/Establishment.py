from dataclasses import dataclass
from src.domain.Address import Address
from dataclasses import field
import uuid


@dataclass
class Establishment:
    """### Represents an establishmemt."""

    
    name: str
    production_time: int
    address: Address
    prompt: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))