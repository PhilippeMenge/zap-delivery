from src.domain.Operator import Operator
from src.infrastructure.repositories.establishment_repository import (
    EstablishmentRepository,
)
from src.infrastructure.repositories.operator_repository import OperatorRepository
from src.utils.auth import validate_password, oauth2_scheme, get_operator_email_from_token
from src.utils.logging import get_configured_logger
from fastapi import Depends, HTTPException, status
from typing import Annotated


logger = get_configured_logger(__name__)


class OperatorService:
    def __init__(
        self,
        operatorRepository: OperatorRepository,
        establishmentRepository: EstablishmentRepository,
    ):
        self._operatorRepository = operatorRepository
        self._establishmentRepository = establishmentRepository

    def get_operator_from_email(self, email: str) -> Operator | None:
        """### Get an operator from an email

        Args:
            email (str): The email of the operator

        Returns:
            Operator: The operator instance. None if not found.
        """
        logger.debug(f"Getting operator from email {email}")
        return self._operatorRepository.get_operator_from_email(email)

    def authenticate_user(self, email: str, password: str) -> Operator | None:
        """### Authenticates a user.

        Args:
            email (str): The user's email.
            password (str): The user's password.

        Returns:
            User: The user instance. None if not found or invalid password.
        """
        logger.debug(f"Authenticating user {email}")
        operator = self.get_operator_from_email(email)

        if operator is None:
            logger.error(f"User {email} not found.")

            return None

        if not validate_password(password, operator.hashed_password):
            logger.error(f"Invalid password for user {email}.")

            return None

        logger.info(f"User {email} authenticated successfully.")

        return operator

    def create_operator(self, operator: Operator, establishment_id: str):
        """### Create an operator.

        If the operator already exists, it will be updated.

        Args:
            operator (Operator): The operator to create.
        """
        establishment = self._establishmentRepository.get_establishment(
            establishment_id
        )
        operator.establishment = establishment
        logger.debug(f"Creating operator {operator.email}")
        self._operatorRepository.create_operator(operator)
        
    
    def get_current_operator(self, token: Annotated[str, Depends(oauth2_scheme)]):
        """### Get the current operator.

        Args:
            token (str): The JWT token.

        Returns:
            Operator: The operator instance.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        
        operator_email = get_operator_email_from_token(token)
        
        if operator_email is None:
            raise credentials_exception
        
        operator = self.get_operator_from_email(operator_email)

        if operator is None:
            raise credentials_exception
        
        return operator

