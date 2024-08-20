import app_logger as log
from database.defs_base import get_bonds, add_bonds_yield
from database.db_start import db_conn, BondsYield
from config_reader import UserParams
import datetime
from tqdm import tqdm
from collections import namedtuple


log = log.get_logger(__name__)
Yield = namedtuple('CouponSums',
                         ['maturity_coupons_sum',
                          'offer_coupon_sum',
                          'last_coupon_sum',
                          'last_coupon_date',
                          'coupon_type'])


async def bonds_yield():
    log.info('start bonds yield')
    con = db_conn()
    bonds = get_bonds(conn=con)
    log.debug(f'Получено {len(bonds)} облигаций')
    rows = []
    for b in tqdm(bonds):
        if b.currency != 'rub':
            continue
        if not b.coupons:
            continue
        else:
            if b.coupons.coupons_sum == 0:
                log.error(f'по облигации {b.ticker} отсутствуют купоны')
                continue
        if not b.last_price:
            log.error(f'по облигации {b.ticker} отсутствует цена')
            continue
        offer_date = datetime.datetime(year=1970, month=1, day=1).date()
        if b.offer:
            offer_date = b.offer.oferta_date
        yield_calculate()
        rows.append(
            BondsYield(
                ticker=b.ticker,
                uid=b.uid,
                last_price=price,
                aci_value=b.aci_value,
                name=b.name,
                val=val,
                profit=profit,
                annual_yield=annual_yield,
                risk_level=b.risk_level,
                maturity_date=b.maturity_date,
                nominal=b.nominal,
                oferta=offer_date,
                floating_coupon_flag=b.floating_coupon_flag,
                amortization_flag=b.amortization_flag,
                last_coupon_date=b.coupons.coupon_date,
                days_to_maturity=date_delta,
            )
        )
    con.close()
    add_bonds_yield(rows)


def yield_calculate(bond):
    price = bond.last_price.price / 100 * bond.nominal
    invest = (price + bond.aci_value)
    val = (bond.nominal + bond.coupons.coupons_sum) - invest
    profit = val / invest
    if bond.floating_coupon_flag:
        date_ = bond.coupons.coupon_date
        if (date_ - datetime.datetime.now().date()).days == 0:
            date_delta = 1
        else:
            date_delta = (date_ - datetime.datetime.now().date()).days
    else:
        if bond.offer:  # and not UserParams().only_maturity:
            date_ = bond.offer.oferta_date
        else:
            date_ = bond.maturity_date
        if (date_ - datetime.datetime.now().date()).days == 0:
            date_delta = 1
        else:
            date_delta = (date_ - datetime.datetime.now().date()).days
    annual_yield = profit / date_delta * 365