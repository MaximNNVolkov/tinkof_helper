from tinkoff.invest import Client
from tinkoff.invest.constants import INVEST_GRPC_API
from tinkoff.invest.schemas import RiskLevel
from tinkoff.invest.utils import quotation_to_decimal
from utils.token import TOKEN
import datetime


class Bond:
    def __init__(self, name: str, ticker: str, uid: str, nominal: float, initial_nominal: float,
                 coupon_quantity_per_year: int, maturity_date: str, aci_value: float, floating_coupon_flag: str,
                 amortization_flag: str, risk_level: RiskLevel):
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

    def get_coupons(self):
        with Client(TOKEN, target=INVEST_GRPC_API) as client:
            self.cuopons = client.instruments.get_bond_coupons(instrument_id=self.uid).events

    # def get_instrument(self):
    #     with Client(TOKEN, target=INVEST_GRPC_API) as client:
    #         self.instrument = client.instruments.get_instrument_by(id=self.uid,
    #                                                                id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_UID).instrument

    def get_last_price(self):
        with Client(TOKEN, target=INVEST_GRPC_API) as client:
            last_price = client.market_data.get_last_prices(instrument_id=[self.uid]).last_prices[0].price
            self.last_price = float(quotation_to_decimal(last_price)) / 100 * self.nominal

    def coupon_fix(self):
        s = 0
        co = 0
        for c in self.cuopons:
            if c.fix_date.date() > datetime.datetime.now().date():
                s = float(quotation_to_decimal(c.pay_one_bond))
                co += 1
        if s > 0:
            self.invest = (self.last_price + self.aci_value)
            self.val = (self.nominal + s) - self.invest
            self.profit = self.val / self.invest
            self.annual_yield = self.profit / (self.maturity_date.date() - datetime.datetime.now().date()).days * 365
