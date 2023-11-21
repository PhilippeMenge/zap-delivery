from sqlalchemy.orm import Session

from src.domain.User import User
from src.infrastructure.models.UserModel import UserModel
from src.domain.Establishment import Establishment


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_user_from_phone_number(self, phone_number: str, establishment: Establishment) -> User | None:
        """### Get a user from a phone number

        Args:
            phone_number (str): The phone number of the user
            establishment (Establishment): The establishment the user is associated with

        Returns:
            User: The user instance. None if not found.
        """
        user_model = (
            self.session.query(UserModel)
            .filter_by(phone_number=phone_number, establishment_id=establishment.id)
            .first()
        )
        if user_model is None:
            return None
        return user_model.to_entity()

    def get_phone_number_from_thread_id(self, thread_id: str) -> str | None:
        """### Get a phone number from a thread ID

        Args:
            thread_id (str): The thread ID

        Returns:
            str: The phone number. None if not found.
        """
        user_model = (
            self.session.query(UserModel).filter_by(thread_id=thread_id).first()
        )
        if user_model is None:
            return None
        return user_model.phone_number

    def get_user_from_thread_id(self, thread_id: str) -> User | None:
        """### Get a user from a thread ID

        Args:
            thread_id (str): The thread ID

        Returns:
            User: The user instance. None if not found.
        """
        user_model = (
            self.session.query(UserModel).filter_by(thread_id=thread_id).first()
        )
        if user_model is None:
            return None
        return user_model.to_entity()

    def create_user(self, user: User):
        """### Create a user.

        If the user already exists, it will be updated.

        Args:
            user (User): The user to create.
        """
        user_model = UserModel.from_entity(user)
        self.session.merge(user_model)
        self.session.commit()
