from sqlalchemy import Column, Integer, String, DateTime, Date, Float, Boolean
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.orm import relationship
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


class BondsYield(DeclarativeBase):
    __tablename__ = 'bonds_yield'

    date = Column(DateTime(), default=datetime.now)
    ticker = Column(String, primary_key=True)
    uid = Column(String)
    last_price = Column(Float)
    aci_value = Column(Float)
    name = Column(String)
    val = Column(Float)
    profit = Column(Float)
    annual_yield = Column(Float)
    risk_level = Column(Integer)
    maturity_date = Column(Date)
    nominal = Column(Float)
    oferta = Column(Date)
    floating_coupon_flag = Column(Boolean)
    amortization_flag = Column(Boolean)
    last_coupon_date = Column(Date)
    days_to_maturity = Column(Integer)


class Currencies(DeclarativeBase):
    __tablename__ = 'currencies'

    date = Column(DateTime(), default=datetime.now)
    ticker = Column(String, primary_key=True)
    uid = Column(String)
    iso_currency_name = Column(String)
    price = Column(Float)


class Prices(DeclarativeBase):
    __tablename__ = 'prices'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime(), default=datetime.now)
    uid = Column(String, ForeignKey('bonds.uid'))
    price = Column(Float)


class Coupons(DeclarativeBase):
    __tablename__ = 'coupons'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime(), default=datetime.now)
    uid = Column(String, ForeignKey('bonds.uid'))
    maturity_coupons_sum = Column(Float)
    offer_coupon_sum = Column(Float)
    last_coupon_sum = Column(Float)
    last_coupon_date = Column(Date)
    coupon_type = Column(Integer)


class Bonds(DeclarativeBase):
    __tablename__ = 'bonds'

    date = Column(DateTime(), default=datetime.now)
    name = Column(String)
    ticker = Column(String)
    uid = Column(String, primary_key=True)
    nominal = Column(Float)
    initial_nominal = Column(Float)
    coupon_quantity_per_year = Column(Float)
    maturity_date = Column(Date)
    aci_value = Column(Float)
    floating_coupon_flag = Column(Boolean)
    amortization_flag = Column(Boolean)
    risk_level = Column(Integer)
    currency = Column(String)
    last_price = relationship('Prices', backref='bonds', uselist=False)
    offer = relationship('OfertaDates', backref='bonds', uselist=False)
    coupons = relationship('Coupons', backref='bonds', uselist=False)


class OfertaDates(DeclarativeBase):
    __tablename__ = 'oferta_dates'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime(), default=datetime.now)
    uid = Column(String, ForeignKey('bonds.uid'))
    oferta_date = Column(Date)


def db_conn():
    engine = create_engine(url_object)
    DeclarativeBase.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session
