from fastapi import APIRouter, Path
from typing import Annotated
from fastapi.requests import Request
from src.domain.Operator import Operator
from src.domain.Order import OrderStatus
from fastapi.responses import Response
from src.utils.auth import hash_password, validate_password, generate_token
from src.utils.logging import get_configured_logger
from pydantic import BaseModel
from src.routers.common import OPERATOR_SERVICE

logger = get_configured_logger(__name__)

router = APIRouter()


class CreateOperatorSchema(BaseModel):
    email: str
    name: str
    password: str
    establishment_id: str


@router.post("/signup")
def create_operator(create_operator_schema: CreateOperatorSchema):
    """### Updates the status of an order."""
    logger.debug("Received request to create operator.")

    email = create_operator_schema.email
    name = create_operator_schema.name
    password = create_operator_schema.password
    establishment_id = create_operator_schema.establishment_id

    hashed_password = hash_password(password)

    operator = Operator(
        email=email,
        name=name,
        hashed_password=hashed_password,
        is_active=True
    )

    OPERATOR_SERVICE.create_operator(operator, establishment_id)

    return Response(status_code=201)


class LoginOperatorSchema(BaseModel):
    email: str
    password: str

@router.post("/login")
def login_operator(login_operator_schema: LoginOperatorSchema):
    """### Updates the status of an order."""
    logger.debug("Received request to login operator.")

    email = login_operator_schema.email
    password = login_operator_schema.password

    operator = OPERATOR_SERVICE.get_operator_from_email(email)

    if operator is None:
        return Response(status_code=401)

    if not operator.is_active:
        return Response(status_code=401)

    if not validate_password(password, operator.hashed_password):
        return Response(status_code=401)
    
    token = generate_token(email)

    return {"token": token}
