from src.domain.Establishment import Establishment
from src.infrastructure.models.AddressModel import AddressModel
from src.infrastructure.init_db import Base
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class EstablishmentModel(Base):
    __tablename__ = "RESTAURANTS"


    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    production_time: Mapped[str] = mapped_column(Integer)
    prompt: Mapped[str] = mapped_column(String(255))
    address_id: Mapped[str] = mapped_column(String(255), ForeignKey("ADDRESSES.id"))
    address = relationship("AddressModel", back_populates="establishment")
    

    def to_entity(self):
        return Establishment(
            id = self.id,
            name = self.name,
            production_time = self.production_time,
            address = self.address.to_entity(),
            prompt = self.prompt
        )

    @staticmethod
    def from_entity(establishment: Establishment):
        return EstablishmentModel(
            id = establishment.id,
            name = establishment.name,
            production_time = establishment.production_time,
            address = AddressModel.from_entity(establishment.address),
            prompt = establishment.prompt
        )