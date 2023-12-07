import uuid
from dataclasses import dataclass, field

from src.domain.Establishment import Establishment, SafeEstablishment


@dataclass
class SafeOperator:
    """### Represents an operator."""

    id: str
    name: str
    email: str
    establishment: SafeEstablishment
    is_active: bool


@dataclass
class Operator:
    """### Represents an operator."""

    email: str
    name: str
    hashed_password: str
    is_active: bool
    establishment: Establishment | None = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_safe(self) -> SafeOperator:
        """### Returns a safe version of the operator."""
        return SafeOperator(
            id=self.id,
            name=self.name,
            email=self.email,
            establishment=self.establishment.to_safe(),
            is_active=self.is_active,
        )
