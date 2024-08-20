from tinkoff.invest import Client
from tinkoff.invest.constants import INVEST_GRPC_API
from tinkoff.invest.schemas import RiskLevel, GetBondEventsRequest, EventType
from tinkoff.invest.utils import quotation_to_decimal
from utils.token import TOKEN
from utils.bonds.card_bond import CardBond
import datetime
import pandas as pd
import app_logger as log
from database.defs_base import get_coupon, get_price, get_currency


log = log.get_logger(__name__)


class Bond:

    def __init__(self, name: str, ticker: str, uid: str, nominal: float, initial_nominal: float,
                 coupon_quantity_per_year: int, maturity_date: datetime, aci_value: float, floating_coupon_flag: bool,
                 amortization_flag: bool, risk_level: RiskLevel, currency: str):
        self.name = name
        self.ticker = ticker
        self.uid = uid
        self.nominal = nominal
        self.initial_nominal = initial_nominal
        self.coupon_quantity_per_year = coupon_quantity_per_year
        self.maturity_date = maturity_date
        self.aci_value = aci_value
        self.floating_coupon_flag = floating_coupon_flag
        self.amortization_flag = amortization_flag
        self.risk_level = risk_level
        self.floating_coupon_flag = floating_coupon_flag
        self.amortization_flag = amortization_flag
        self.currency = currency


    def get_bonds_event(self):
        with Client(TOKEN, target=INVEST_GRPC_API) as client:
            self.bond_event = client.instruments.get_bond_events(request=GetBondEventsRequest(
                instrument_id=self.uid, type=EventType.EVENT_TYPE_CALL,
                from_=datetime.datetime.now(), to=self.maturity_date,
            ))
            self.oferta = None
            df = pd.DataFrame(self.bond_event.events)
            if not(df.empty):
                self.oferta = df[df.event_type == 2].pay_date.iloc[0].date()


    def get_last_price(self):
        price = get_price(self.uid).price
        if self.currency != 'rub':
            cur_value = get_currency(iso_currency_name=self.currency)
            self.last_price = price / 100 * self.nominal * cur_value
            self.nominal = self.nominal * cur_value
            self.aci_value = self.aci_value * cur_value
        else:
            self.last_price = price / 100 * self.nominal


    def get_coupon_value(self):
        coupon = get_coupon(self.uid)
        s = coupon.coupons_sum
        if self.currency != 'rub':
            s = s * get_currency(iso_currency_name=self.currency)
        self.last_coupon_date = coupon.coupon_date
        return s


    def coupon_fixed(self, sum_coupons: float):
        log.info(f'{self.ticker} fixed coupon')
        self.invest = (self.last_price + self.aci_value)
        self.val = (self.nominal + sum_coupons) - self.invest
        self.profit = self.val / self.invest
        if self.oferta:
            date_ = self.oferta.date()
        else:
            date_ = self.maturity_date.date()
        if (date_ - datetime.datetime.now().date()).days == 0:
            date_delta = 1
        else:
            date_delta = (date_ - datetime.datetime.now().date()).days
        self.annual_yield = self.profit / date_delta * 365


    def coupon_floating(self, sum_coupons: float):
        log.info(f'{self.ticker} floating coupon')
        self.invest = (self.last_price + self.aci_value)
        self.val = (self.nominal + sum_coupons) - self.invest
        self.profit = self.val / self.invest
        date_ = self.last_coupon_date
        if (date_ - datetime.datetime.now().date()).days == 0:
            date_delta = 1
        else:
            date_delta = (date_ - datetime.datetime.now().date()).days
        self.annual_yield = self.profit / date_delta * 365
