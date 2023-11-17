from dataclasses import dataclass
from src.domain.Establishment import Establishment


@dataclass
class UserThread:
    """### Represents the relationship between a user and an openai thread."""

    phone_number: str
    thread_id: str
    establishment: Establishment
