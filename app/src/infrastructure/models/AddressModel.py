from src.domain.Address import Address
from src.infrastructure.init_db import Base
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class AddressModel(Base):
    __tablename__ = "ADDRESSES"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    street: Mapped[str] = mapped_column(String(255))
    number: Mapped[str] = mapped_column(String(255))
    complement: Mapped[str] = mapped_column(String(255), nullable=True)
    neighborhood: Mapped[str] = mapped_column(String(255))
    city: Mapped[str] = mapped_column(String(255))
    state: Mapped[str] = mapped_column(String(255))
    country: Mapped[str] = mapped_column(String(255))
    zipcode: Mapped[str] = mapped_column(String(255))
    orders = relationship("OrderModel", back_populates="address")
    establishment = relationship("EstablishmentModel", back_populates="address")

    def to_entity(self):
        return Address(
            id=self.id,
            street=self.street,
            number=self.number,
            complement=self.complement,
            city=self.city,
            state=self.state,
            country=self.country,
            zipcode=self.zipcode,
            neighborhood=self.neighborhood,
        )

    @staticmethod
    def from_entity(address: Address):
        return AddressModel(
            id=address.id,
            street=address.street,
            number=address.number,
            complement=address.complement,
            city=address.city,
            state=address.state,
            country=address.country,
            zipcode=address.zipcode,
            neighborhood=address.neighborhood,
        )
