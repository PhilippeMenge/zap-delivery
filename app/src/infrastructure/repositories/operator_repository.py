from sqlalchemy.orm import Session
from src.domain.Establishment import Establishment
from src.domain.Operator import Operator
from src.infrastructure.models.OperatorModel import OperatorModel
from src.infrastructure.repositories.establishment_repository import (
    EstablishmentRepository,
)


class OperatorRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_operator_from_email(self, email: str) -> Operator | None:
        """### Get an operator from an email

        Args:
            email (str): The email of the operator

        Returns:
            Operator: The operator instance. None if not found.
        """
        operator_model = (
            self.session.query(OperatorModel).filter_by(email=email).first()
        )
        if operator_model is None:
            return None
        return operator_model.to_entity()

    def update_operator(self, operator: Operator):
        """### Update an operator.

        If the operator does not exist, it will be created.

        Args:
            operator (Operator): The operator to update.
        """
        operator_model = OperatorModel.from_entity(operator)
        self.session.merge(operator_model)
        self.session.commit()

    def create_operator(self, operator: Operator):
        """### Create an operator.

        If the operator already exists, it will be updated.

        Note: This method is a wrapper around `update_operator`.

        Args:
            operator (Operator): The operator to create.
        """
        self.update_operator(operator)
