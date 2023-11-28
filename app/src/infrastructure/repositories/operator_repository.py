from sqlalchemy.orm import Session

from src.domain.Operator import Operator
from src.infrastructure.models.OperatorModel import OperatorModel
from src.infrastructure.repositories.establishment_repository import EstablishmentRepository
from src.domain.Establishment import Establishment


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
        operator_model = self.session.query(OperatorModel).filter_by(email=email).first()
        if operator_model is None:
            return None
        return operator_model.to_entity()

    def create_operator(self, operator: Operator):
        """### Create an operator.

        If the operator already exists, it will be updated.

        Args:
            operator (Operator): The operator to create.
        """
        operator_model = OperatorModel.from_entity(operator)
        self.session.merge(operator_model)
        self.session.commit()
