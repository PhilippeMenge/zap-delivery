from src.domain.UserThread import UserThread
from app.src.infrastructure.models.EstablishmentModel import EstablishmentModel
from src.infrastructure.init_db import Base
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class UserThreadModel(Base):
    __tablename__ = "USER_THREADS"

    phone_number: Mapped[str] = mapped_column(String(255), primary_key=True)
    thread_id: Mapped[str] = mapped_column(String(255))
    establishment_id: Mapped[str] = mapped_column(String(255), ForeignKey("ESTABLISHMENTS.id"))   
     
    establishment = relationship("EstablishmentModel", back_populates="user_thread")
    orders = relationship("OrderModel", back_populates="user_thread")

    def to_entity(self):
        return UserThread(
            phone_number=self.phone_number,
            thread_id=self.thread_id,
            establishment = self.establishment.to_entity()
        )

    @staticmethod
    def from_entity(user_thread: UserThread):
        return UserThreadModel(
            phone_number=user_thread.phone_number,
            thread_id=user_thread.thread_id,
            establishment = EstablishmentModel.from_entity(user_thread.establishment)
        )
