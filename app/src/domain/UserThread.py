from dataclasses import dataclass


@dataclass
class UserThread:
    """### Represents the relationship between a user and an openai thread."""

    phone_number: str
    thread_id: str
