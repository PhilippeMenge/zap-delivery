from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.requests import Request
from fastapi.responses import Response
from pydantic import BaseModel
from src.domain.Operator import Operator
from src.domain.Order import OrderStatus
from src.routers.common import OPERATOR_SERVICE
from src.utils.auth import generate_token, hash_password
from src.utils.logging import get_configured_logger

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
        email=email, name=name, hashed_password=hashed_password, is_active=True
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

    operator = OPERATOR_SERVICE.authenticate_user(email, password)

    if operator is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = generate_token({"sub": operator.email})

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me")
def get_operator_me(request: Request, current_user: Operator = Depends(OPERATOR_SERVICE.get_current_operator)):
    """### Get the current operator."""
    logger.debug("Received request to get current operator.")

    return {"operator": current_user.email}