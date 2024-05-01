from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import pandas as pd


url_object = URL.create(
    "sqlite",
    username="",
    password="",
    host="",
    database="tinkoff.db",
)


engine = create_engine(url_object)
DeclarativeBase = declarative_base()


class Users(DeclarativeBase):
    __tablename__ = 'users'

    user_id = Column('user_id', Integer, primary_key=True)
    date = Column(DateTime(), default=datetime.now)
    first_name = Column('first_name', String)
    last_name = Column('last_name', String)
    user_name = Column('user_name', String)

    def __repr__(self):
        return f"<user_id={self.user_id}," \
               f"first_name={self.first_name}," \
               f"last_name={self.last_name}," \
               f"user_name={self.user_name}>"

    @property
    def serialize(self):
        return {
            'user_id': self.user_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'user_name': self.user_name
        }


class Instruments(DeclarativeBase):
    __tablename__ = 'instruments'

    date = Column(DateTime(), default=datetime.now)
    ticker = Column(String, primary_key=True)
    class_code = Column(String)
    figi = Column(String)
    uid = Column(String)
    type = Column(String)
    name = Column(String)


def db_conn():
    engine = create_engine(url_object)
    DeclarativeBase.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session
