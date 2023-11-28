from src.domain.Operator import Operator
from src.infrastructure.repositories.operator_repository import OperatorRepository
from src.infrastructure.repositories.establishment_repository import EstablishmentRepository
from src.utils.logging import get_configured_logger

logger = get_configured_logger(__name__)


class OperatorService:
    def __init__(
        self,
        operatorRepository: OperatorRepository,
        establishmentRepository: EstablishmentRepository
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
    
    def create_operator(self, operator: Operator, establishment_id: str):
        """### Create an operator.

        If the operator already exists, it will be updated.

        Args:
            operator (Operator): The operator to create.
        """
        establishment = self._establishmentRepository.get_establishment(establishment_id)
        operator.establishment = establishment
        logger.debug(f"Creating operator {operator.email}")
        self._operatorRepository.create_operator(operator)