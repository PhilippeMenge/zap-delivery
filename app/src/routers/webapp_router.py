from fastapi import APIRouter, Path
from typing import Annotated
from fastapi.requests import Request
from src.domain.Order import OrderStatus
from fastapi.responses import Response
from src.routers.common import ORDER_SERVICE
from src.utils.logging import get_configured_logger
from pydantic import BaseModel

logger = get_configured_logger(__name__)

router = APIRouter()


@router.get("/orders")
def get_orders(establishment_id: str):
    """### Returns all orders."""
    logger.debug("Received request to get all orders.")
    return ORDER_SERVICE.get_orders_by_establishment_id(establishment_id)


class OrderStatusUpdate(BaseModel):
    status: str


@router.post("/orders/{order_id}/update-status")
def update_order_status(order_id: Annotated[str, Path(title="The id of the order.")], status_update: OrderStatusUpdate):
    """### Updates the status of an order."""
    logger.debug("Received request to update order status.")
    
    status_str = status_update.status
    status = OrderStatus(status_str)
    
    ORDER_SERVICE.update_order_status(order_id, status)
    return Response(status_code=200)