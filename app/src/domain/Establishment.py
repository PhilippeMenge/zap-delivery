from dataclasses import dataclass
from src.domain.Address import Address


@dataclass
class Establishment:
    """### Represents an establishmemt."""

    id: str
    name: str
    production_time: int
    address: Address
    prompt: str