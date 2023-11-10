from sqlalchemy.orm import Session

from infrastructure.models.UserThreadModel import UserThreadModel
from domain.UserThread import UserThread

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

    def create_user_thread(self, user_thread: UserThread):
        """### Create a user thread.
        
        If the user thread already exists, it will be updated.
        
        Args:
            user_thread (UserThread): The user thread to create.
        """
        user_thread_model = UserThreadModel.from_entity(user_thread)
        self.session.merge(user_thread_model)
        self.session.commit()
        