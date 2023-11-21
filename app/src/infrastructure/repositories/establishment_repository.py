from sqlalchemy.orm import Session
from src.domain.Establishment import Establishment
from src.infrastructure.models.EstablishmentModel import EstablishmentModel


class EstablishmentRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_establishment_from_whatsapp_phone_number_id(
        self, whatsapp_number_id: int
    ) -> Establishment | None:
        """### Get an establishment from a WhatsApp phone number ID

        Args:
            whatsapp_phone_number_id (int): The WhatsApp phone number ID

        Returns:
            Establishment: The establishment instance. None if not found.
        """

        establishment_model = (
            self.session.query(EstablishmentModel)
            .filter_by(whatsapp_number_id=whatsapp_number_id)
            .first()
        )

        if establishment_model is None:
            return None

        return establishment_model.to_entity()

    def create_establishment(self, establishment: Establishment):
        """### Create an establishment

        Args:
            establishment (Establishment): The establishment to create.
        """
        establishment_model = EstablishmentModel.from_entity(establishment)

        self.session.merge(establishment_model)
        self.session.commit()
