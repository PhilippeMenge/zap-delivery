from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.responses import Response
from pydantic import BaseModel
from src.domain.MenuItem import MenuItem
from src.domain.Operator import Operator
from src.domain.Order import OrderStatus
from src.routers.common import MENU_ITEMS_SERVICE, OPERATOR_SERVICE, ORDER_SERVICE
from src.utils.logging import get_configured_logger

logger = get_configured_logger(__name__)

router = APIRouter()


@router.get("/orders")
def get_orders(operator: Operator = Depends(OPERATOR_SERVICE.get_current_operator)):
    """### Returns all orders."""
    logger.debug("Received request to get all orders.")

    establishment = operator.establishment

    if establishment is None:
        raise HTTPException(status_code=400, detail="Operator has no establishment.")

    safe_orders = [
        order.to_safe()
        for order in ORDER_SERVICE.get_orders_by_establishment_id(establishment.id)
    ]

    return safe_orders


class OrderStatusUpdate(BaseModel):
    status: str


@router.post("/orders/{order_id}/update-status")
def update_order_status(
    order_id: Annotated[str, Path(title="The id of the order.")],
    status_update: OrderStatusUpdate,
):
    """### Updates the status of an order."""
    logger.debug("Received request to update order status.")

    status_str = status_update.status
    status = OrderStatus(status_str)

    ORDER_SERVICE.update_order_status(order_id, status)
    return Response(status_code=200)


@router.get("/menu-items/")
def get_menu_items(operator: Operator = Depends(OPERATOR_SERVICE.get_current_operator)):
    """### Returns all menu items."""
    logger.debug("Received request to get all menu items.")

    establishment = operator.establishment

    if establishment is None:
        raise HTTPException(status_code=400, detail="Operator has no establishment.")

    menu_items = MENU_ITEMS_SERVICE.get_all_menu_items_by_establishment(establishment)

    safe_menu_items = [menu_item.to_safe() for menu_item in menu_items]

    return {"menu_items": safe_menu_items}


class MenuItemUpdate(BaseModel):
    name: str
    price: str
    description: str


@router.put("/menu-items/{menu_item_id}/")
def update_menu_item(
    menu_item_id: Annotated[str, Path(title="The id of the menu item.")],
    menu_item_update: MenuItemUpdate,
    operator: Operator = Depends(OPERATOR_SERVICE.get_current_operator),
):
    """### Updates a menu item."""
    logger.debug("Received request to update menu item.")

    establishment = operator.establishment

    if establishment is None:
        raise HTTPException(status_code=400, detail="Operator has no establishment.")

    menu_item = MENU_ITEMS_SERVICE.get_menu_item_by_id(menu_item_id, establishment)

    if menu_item is None:
        raise HTTPException(status_code=404, detail="Menu item not found.")

    menu_item.name = menu_item_update.name
    menu_item.price = menu_item_update.price
    menu_item.description = menu_item_update.description

    MENU_ITEMS_SERVICE.update_menu_item(menu_item)
    return Response(status_code=200)
