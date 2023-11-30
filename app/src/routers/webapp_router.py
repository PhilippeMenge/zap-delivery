from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.responses import Response
from pydantic import BaseModel
from src.domain.Operator import Operator
from src.domain.Order import OrderStatus
from src.routers.common import OPERATOR_SERVICE, ORDER_SERVICE
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

    return ORDER_SERVICE.get_orders_by_establishment_id(establishment.id)


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
