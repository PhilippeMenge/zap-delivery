from domain.UserThread import UserThread
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.init_db import Base


class UserThreadModel(Base):
    __tablename__ = "users"

    phone_number: Mapped[str] = mapped_column(String(255), primary_key=True)
    thread_id: Mapped[str] = mapped_column(String(255))

    def to_entity(self):
        return UserThread(
            phone_number=self.phone_number,
            thread_id=self.thread_id,
        )

    @staticmethod
    def from_entity(user_thread: UserThread):
        return UserThreadModel(
            phone_number=user_thread.phone_number,
            thread_id=user_thread.thread_id,
        )
