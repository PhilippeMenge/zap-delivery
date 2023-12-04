from dataclasses import dataclass
from src.domain.Establishment import Establishment, SafeEstablishment



@dataclass
class SafeUser:
    """### Represents the relationship between a user and an openai thread."""

    phone_number: str
    thread_id: str
    establishment: SafeEstablishment
@dataclass
class User:
    """### Represents the relationship between a user and an openai thread."""

    phone_number: str
    thread_id: str
    establishment: Establishment

    def to_safe(self) -> SafeUser:
        """### Returns a safe version of the user."""
        return SafeUser(
            phone_number=self.phone_number,
            thread_id=self.thread_id,
            establishment=self.establishment.to_safe()
        )


