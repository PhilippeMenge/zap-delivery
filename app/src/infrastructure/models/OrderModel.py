import uuid

from src.domain.Order import Order, OrderStatus
from src.domain.OrderItem import OrderItem
from src.infrastructure.init_db import Base
from src.infrastructure.models.AddressModel import AddressModel
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
            order_id=self.order_id,
        )

    @staticmethod
    def from_entity(order_item: OrderItem):
        return OrderItemModel(
            id_item=order_item.menu_item.id,
            amount=order_item.amount,
            observation=order_item.observation,
            order_id=order_item.order_id,
        )


class OrderModel(Base):
    __tablename__ = "ORDERS"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    status: Mapped[str] = mapped_column(String(255))
    checkout_session_id: Mapped[str] = mapped_column(String(255), nullable=True)
    user_phone_number: Mapped[str] = mapped_column(
        String(255), ForeignKey("USER_THREADS.phone_number")
    )
    address_id: Mapped[str] = mapped_column(String(255), ForeignKey("ADDRESSES.id"))
    address = relationship("AddressModel", back_populates="orders")
    user_thread = relationship("UserThreadModel", back_populates="orders")
    order_items = relationship("OrderItemModel", back_populates="order")

    def to_entity(self):
        return Order(
            id=self.id,
            address=self.address.to_entity(),
            status=OrderStatus(self.status),
            checkout_session_id=self.checkout_session_id,
            user_thread=self.user_thread.to_entity(),
            itens=[order_item.to_entity() for order_item in self.order_items],
        )

    @staticmethod
    def from_entity(order: Order):
        return OrderModel(
            id=str(order.id),
            address=AddressModel.from_entity(order.address),
            status=order.status.value,
            checkout_session_id=order.checkout_session_id,
            user_phone_number=order.user_thread.phone_number,
            order_items=[
                OrderItemModel.from_entity(order_item) for order_item in order.itens
            ],
        )
