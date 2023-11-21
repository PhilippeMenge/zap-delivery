from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.domain.User import User
from src.infrastructure.init_db import Base
from src.infrastructure.models.EstablishmentModel import EstablishmentModel


class UserModel(Base):
    __tablename__ = "USERS"

    phone_number: Mapped[str] = mapped_column(String(255), primary_key=True)
    thread_id: Mapped[str] = mapped_column(String(255))
    establishment_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("ESTABLISHMENTS.id")
    )
    establishment = relationship("EstablishmentModel", back_populates="user")
    orders = relationship("OrderModel", back_populates="user")

    def to_entity(self):
        return User(
            phone_number=self.phone_number,
            thread_id=self.thread_id,
            establishment=self.establishment.to_entity(),
        )

    @staticmethod
    def from_entity(user: User):
        return UserModel(
            phone_number=user.phone_number,
            thread_id=user.thread_id,
            establishment=EstablishmentModel.from_entity(user.establishment),
        )
