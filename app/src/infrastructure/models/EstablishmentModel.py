from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.domain.Establishment import Establishment
from src.infrastructure.init_db import Base
from src.infrastructure.models.AddressModel import AddressModel


class EstablishmentModel(Base):
    __tablename__ = "ESTABLISHMENTS"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    estimated_production_minutes: Mapped[int] = mapped_column(Integer)
    custom_prompt_section: Mapped[str] = mapped_column(String(255))
    whatsapp_api_key: Mapped[str] = mapped_column(String(255))
    whatsapp_number_id: Mapped[str] = mapped_column(String(255))
    contact_number: Mapped[str] = mapped_column(String(255))

    address_id: Mapped[str] = mapped_column(String(255), ForeignKey("ADDRESSES.id"))
    address = relationship("AddressModel")
    user = relationship("UserModel", back_populates="establishment")
    menu_items = relationship("MenuItemModel", back_populates="establishment")
    operators = relationship("OperatorModel", back_populates="establishment")

    def to_entity(self):
        return Establishment(
            id=self.id,
            name=self.name,
            whatsapp_api_key=self.whatsapp_api_key,
            whatsapp_number_id=self.whatsapp_number_id,
            contact_number=self.contact_number,
            estimated_production_minutes=self.estimated_production_minutes,
            custom_prompt_section=self.custom_prompt_section,
            address=self.address.to_entity(),
        )

    @staticmethod
    def from_entity(establishment: Establishment):
        return EstablishmentModel(
            id=establishment.id,
            name=establishment.name,
            estimated_production_minutes=establishment.estimated_production_minutes,
            whatsapp_api_key=establishment.whatsapp_api_key,
            whatsapp_number_id=establishment.whatsapp_number_id,
            contact_number=establishment.contact_number,
            custom_prompt_section=establishment.custom_prompt_section,
            address=AddressModel.from_entity(establishment.address),
        )
