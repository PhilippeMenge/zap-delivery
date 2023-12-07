from datetime import timedelta
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
    """### Create operator."""
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
    """### Login operator."""
    logger.debug("Received request to login operator.")

    email = login_operator_schema.email
    password = login_operator_schema.password

    operator = OPERATOR_SERVICE.authenticate_user(email, password)

    if operator is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = generate_token(
        {"sub": operator.email}, expires_delta=timedelta(hours=36)
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/refresh")
def refresh_token(
    current_user: Operator = Depends(OPERATOR_SERVICE.get_current_operator),
):
    """### Refresh token."""
    logger.debug("Received request to refresh token.")

    access_token = generate_token(
        {"sub": current_user.email}, expires_delta=timedelta(hours=36)
    )

    return {"access_token": access_token, "token_type": "bearer"}


class UpdateOperator(BaseModel):
    name: str | None = None
    password: str | None = None


@router.put("/me/update-operator")
def update_operator(
    update_operator: UpdateOperator,
    operator: Operator = Depends(OPERATOR_SERVICE.get_current_operator),
):
    """### Updates the operator."""
    logger.debug("Received request to update operator.")

    operator.name = (
        update_operator.name if update_operator.name is not None else operator.name
    )
    operator.hashed_password = (
        hash_password(update_operator.password)
        if update_operator.password is not None
        else operator.hashed_password
    )

    OPERATOR_SERVICE.update_operator(operator)
    return Response(status_code=200)


@router.get("/me")
def get_operator_me(
    current_user: Operator = Depends(OPERATOR_SERVICE.get_current_operator),
):
    """### Get the current operator."""
    logger.debug("Received request to get current operator.")

    return {"operator": current_user.to_safe()}
