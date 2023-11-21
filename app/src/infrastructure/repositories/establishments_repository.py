from src.domain.Establishment import Establishment
from src.infrastructure.models.EstablishmentModel import EstablishmentModel
from sqlalchemy.orm import Session


class EstablishmentsRepository:
    def __init__(self, session: Session):
        self.session = session