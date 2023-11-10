from infrastructure.models.UserThreadModel import UserThreadModel
from infrastructure.init_db import Base
from sqlalchemy import create_engine


def main():
    engine = create_engine("sqlite:///db.sqlite3", echo=True)
    Base.metadata.create_all(bind=engine)
    client_phone_number = input("Enter your phone number: ")


if __name__ == "__main__":
    main()
