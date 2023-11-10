import uuid

from domain.Order import Order, OrderStatus
from domain.OrderItem import OrderItem
from infrastructure.init_db import Base
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class OrderItemModel(Base):
    __tablename__ = "ORDER_ITEMS"

    id_item: Mapped[str] = mapped_column(
        String(255), ForeignKey("MENU_ITEMS.id"), primary_key=True
    )
    menu_item = relationship("MenuItemModel")

    amount: Mapped[int] = mapped_column(Integer)
    observation: Mapped[str] = mapped_column(String(255))
    order_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("ORDERS.id"), primary_key=True
    )
    order = relationship("OrderModel", back_populates="order_items")

    def to_entity(self):
        return OrderItem(
            menu_item=self.menu_item.to_entity(),
            amount=self.amount,
            observation=self.observation,
        )

    @staticmethod
    def from_entity(order_item: OrderItem):
        return OrderItemModel(
            id_item=order_item.menu_item.id,
            amount=order_item.amount,
            observation=order_item.observation,
        )


class OrderModel(Base):
    __tablename__ = "ORDERS"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    address: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(255))
    order_items = relationship("OrderItemModel", back_populates="order")

    def to_entity(self):
        return Order(
            id=self.id,
            address=self.address,
            status=OrderStatus(self.status),
            itens=[order_item.to_entity() for order_item in self.order_items],
        )
        
    @staticmethod
    def from_entity(order: Order):
        return OrderModel(
            id=str(order.id),
            address=order.address,
            status=order.status.value,
            order_items=[
                OrderItemModel.from_entity(order_item) for order_item in order.itens
            ],
        )
