from src.domain.UserThread import UserThread
from src.infrastructure.models.UserThreadModel import UserThreadModel
from sqlalchemy.orm import Session


class UserThreadRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_user_thread_from_phone_number(self, phone_number: str) -> UserThread | None:
        """### Get a user thread from a phone number

        Args:
            phone_number (str): The phone number of the user

        Returns:
            UserThread: The user thread instance. None if not found.
        """
        user_thread_model = self.session.query(UserThreadModel).get(phone_number)
        if user_thread_model is None:
            return None
        return user_thread_model.to_entity()

    def get_phone_number_from_thread_id(self, thread_id: str) -> str | None:
        """### Get a phone number from a thread ID

        Args:
            thread_id (str): The thread ID

        Returns:
            str: The phone number. None if not found.
        """
        user_thread_model = (
            self.session.query(UserThreadModel).filter_by(thread_id=thread_id).first()
        )
        if user_thread_model is None:
            return None
        return user_thread_model.phone_number

    def get_user_thread_from_thread_id(self, thread_id: str) -> UserThread | None:
        """### Get a user thread from a thread ID

        Args:
            thread_id (str): The thread ID

        Returns:
            UserThread: The user thread instance. None if not found.
        """
        user_thread_model = (
            self.session.query(UserThreadModel).filter_by(thread_id=thread_id).first()
        )
        if user_thread_model is None:
            return None
        return user_thread_model.to_entity()

    def create_user_thread(self, user_thread: UserThread):
        """### Create a user thread.

        If the user thread already exists, it will be updated.

        Args:
            user_thread (UserThread): The user thread to create.
        """
        user_thread_model = UserThreadModel.from_entity(user_thread)
        self.session.merge(user_thread_model)
        self.session.commit()
