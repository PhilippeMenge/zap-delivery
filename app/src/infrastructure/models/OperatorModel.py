from src.infrastructure.init_db import Base
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.domain.Operator import Operator
from src.infrastructure.models.EstablishmentModel import EstablishmentModel

class OperatorModel(Base):
    __tablename__ = "OPERATORS"

    email: Mapped[str] = mapped_column(String(255), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean)
    establishment_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("ESTABLISHMENTS.id"))
    id: Mapped[str] = mapped_column(String(255))
    establishment = relationship("EstablishmentModel", back_populates="operators")

    def to_entity(self):
        return Operator(
            email=self.email,
            name=self.name,
            hashed_password=self.hashed_password,
            is_active=self.is_active,
            establishment=self.establishment.to_entity(),
            id=self.id
        )
    
    @staticmethod
    def from_entity(operator: Operator):
        return OperatorModel(
            email=operator.email,
            name=operator.name,
            hashed_password=operator.hashed_password,
            is_active=operator.is_active,
            establishment=EstablishmentModel.from_entity(operator.establishment),
            id=operator.id
        )

   