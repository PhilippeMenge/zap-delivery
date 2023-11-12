from domain.Address import Address
from infrastructure.models.AddressModel import AddressModel
from sqlalchemy.orm import Session


class AddressRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_address(self, address_id: str) -> Address | None:
        """### Get an address from its id.

        Args:
            address_id (str): The id of the address.

        Returns:
            Address: The address instance. None if not found.
        """
        address_model = self.session.query(AddressModel).get(address_id)
        if address_model is None:
            return None
        return address_model.to_entity()

    def add_address(self, address: Address):
        """### Add an address.

        Args:
            address (Address): The address to add.
        """
        address_model = AddressModel.from_entity(address)
        self.session.merge(address_model)
        self.session.commit()
