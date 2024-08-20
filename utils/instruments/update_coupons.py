import app_logger as log
from config_reader import config
from tinkoff.invest import AsyncClient
from tinkoff.invest.constants import INVEST_GRPC_API
from tinkoff.invest.utils import quotation_to_decimal
from tinkoff.invest.schemas import GetBondEventsRequest
from database.defs_base import add_coupons, get_bonds, add_offer_date, add_bonds, get_offer_date
from database.db_start import Coupons, OfertaDates, Bonds, db_conn
from collections import namedtuple
import datetime
from tqdm import tqdm
import pandas as pd


log = log.get_logger(__name__)
TOKEN = config.tinkoff_token.get_secret_value()
CouponSums = namedtuple('CouponSums',
                         ['maturity_coupons_sum',
                          'offer_coupon_sum',
                          'last_coupon_sum',
                          'last_coupon_date',
                          'coupon_type'])


async def get_coupon_value():
    log.info(f'загрузка купонов.')
    await load_bonds()
    await get_bonds_event()
    try:
        async with AsyncClient(TOKEN, target=INVEST_GRPC_API) as client:
            con = db_conn()
            bonds = get_bonds(conn=con)
            con.close()
            coupon_rows = []
            for x in tqdm(bonds):
                date_to = datetime.datetime(year=x.maturity_date.year, month=x.maturity_date.month, day=x.maturity_date.day)
                if date_to.year == 1970:
                    date_to = datetime.datetime(year=2099, month=12, day=31)
                cuopons = await client.instruments.get_bond_coupons(instrument_id=x.uid,
                                                                    from_=datetime.datetime.now(),
                                                                    to=date_to)
                try:
                    offer_date = get_offer_date(uid=x.uid).oferta_date
                except Exception as e:
                    offer_date = datetime.datetime(year=2099, month=12, day=31).date()
                cuopon_sums = get_coupon_values(cuopons, x.maturity_date, offer_date)
                coupon_rows.append(Coupons(uid=x.uid,
                                           maturity_coupons_sum=cuopon_sums.maturity_coupons_sum,
                                           offer_coupon_sum=cuopon_sums.offer_coupon_sum,
                                           last_coupon_sum=cuopon_sums.last_coupon_sum,
                                           last_coupon_date=cuopon_sums.last_coupon_date,
                                           coupon_type=cuopon_sums.coupon_type))
            log.info(f'загружено купонов {len(coupon_rows)}')
            add_coupons(coupon_rows)
    except Exception as e:
        print(e)


def get_coupon_values(cuopons, maturity_date: datetime.date, offer_date: datetime.date):
    maturity_coupons_sum = sum([quotation_to_decimal(x.pay_one_bond)
                                for x in cuopons.events
                                if x.coupon_date.date() <= maturity_date])
    offer_coupon_sum = sum([quotation_to_decimal(x.pay_one_bond)
                            for x in cuopons.events
                            if x.coupon_date.date() <= offer_date])
    last_coupon_sum = sum([quotation_to_decimal(x.pay_one_bond)
                           for x in cuopons.events])
    coupon_dates = [x.coupon_date
                    for x in cuopons.events]
    last_coupon_date = None
    if len(coupon_dates) > 0:
        last_coupon_date = coupon_dates[-1]
    coupon_type = None
    if len(cuopons.events) > 0:
        coupon_type = cuopons.events[0].coupon_type
    return CouponSums(maturity_coupons_sum, offer_coupon_sum, last_coupon_sum, last_coupon_date, coupon_type)


async def get_bonds_event():
    log.info(f'загрузка дат оферты.')
    try:
        async with AsyncClient(TOKEN, target=INVEST_GRPC_API) as client:
            con = db_conn()
            bonds = get_bonds(conn=con)
            con.close()
            rows = []
            for b in tqdm(bonds):
                date_to = datetime.datetime(year=b.maturity_date.year, month=b.maturity_date.month,
                                            day=b.maturity_date.day)
                if date_to.year == 1970:
                    date_to = datetime.datetime(year=2199, month=12, day=31)
                bond_event = await client.instruments.get_bond_events(request=GetBondEventsRequest(
                    instrument_id=b.uid,
                    from_=datetime.datetime.now(),
                    to=date_to
                ))
                df = pd.DataFrame(bond_event.events)
                if not df.empty:
                    if len(df[df.event_type == 2]) > 0:
                        offer = df[df.event_type == 2].pay_date.iloc[0]
                        uid = df[df.event_type == 2].instrument_id.iloc[0]
                        rows.append(OfertaDates(oferta_date=offer, uid=uid))
            add_offer_date(rows)
    except Exception as e:
        print(e)


async def load_bonds():
    log.info('Load bonds')
    try:
        async with AsyncClient(TOKEN, target=INVEST_GRPC_API) as client:
            bonds = await client.instruments.bonds()
            bonds = bonds.instruments
            rows = []
            for b in bonds:
                rows.append(Bonds(name=b.name,
                                  ticker=b.ticker,
                                  uid=b.uid,
                                  nominal=float(quotation_to_decimal(b.nominal)),
                                  initial_nominal=float(quotation_to_decimal(b.initial_nominal)),
                                  coupon_quantity_per_year=b.coupon_quantity_per_year,
                                  maturity_date=b.maturity_date,
                                  aci_value=float(quotation_to_decimal(b.aci_value)),
                                  floating_coupon_flag=b.floating_coupon_flag,
                                  amortization_flag=b.amortization_flag,
                                  risk_level=b.risk_level,
                                  currency=b.currency))
            add_bonds(rows)
    except Exception as e:
        print(e)
