from src.domain.MenuItem import MenuItem
from src.infrastructure.models.EstablishmentModel import EstablishmentModel
from src.infrastructure.init_db import Base
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class MenuItemModel(Base):
    __tablename__ = "MENU_ITEMS"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    price: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean)
    establishment_id: Mapped[str] = mapped_column(String(255), ForeignKey("ESTABLISHMENTS.id"))    
    establishment = relationship("EstablishmentModel", back_populates="menu_item")

    def to_entity(self):
        return MenuItem(
            id=self.id,
            name=self.name,
            price=self.price,
            description=self.description,
            is_active=self.is_active,
            establishment = self.establishment.to_entity()
        )

    @staticmethod
    def from_entity(menu_item: MenuItem):
        return MenuItemModel(
            id=menu_item.id,
            name=menu_item.name,
            price=menu_item.price,
            description=menu_item.description,
            is_active=menu_item.is_active,
            establishment = EstablishmentModel.from_entity(menu_item.establishment)
        )
