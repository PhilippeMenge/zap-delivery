from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session
from src.config import DB_URL


class Base(DeclarativeBase):
    pass


def get_db():
    engine = create_engine(DB_URL)
    Base.metadata.create_all(engine)
    db = Session(bind=engine)
    return db
