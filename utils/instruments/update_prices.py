import app_logger as log
from config_reader import config
from tinkoff.invest import AsyncClient
from tinkoff.invest.utils import quotation_to_decimal
from tinkoff.invest.schemas import InstrumentStatus
from database.defs_base import add_currency, add_prices
from database.db_start import Prices
from utils.bonds.bonds_yield import bonds_yield
import time
import pandas as pd


start_time = time.time()
log = log.get_logger(__name__)
TOKEN = config.tinkoff_token.get_secret_value()


async def currencyces():
    try:
        async with AsyncClient(TOKEN) as client:
            currency = await client.instruments.currencies(instrument_status=InstrumentStatus.INSTRUMENT_STATUS_ALL)
        price = await prices()
        for i in currency.instruments:
            if (i.iso_currency_name in ['usd', 'eur', 'cny']) & i.ticker.endswith('TOM'):
                my_cyr = i
                nominal = quotation_to_decimal(my_cyr.nominal)
                iso_currency_name = my_cyr.iso_currency_name
                uid = my_cyr.uid
                cur_price = price[price['uid'] == uid].iloc[0].price
                add_currency({'uid': uid,
                              'ticker': i.ticker,
                              'price': cur_price/nominal,
                              'iso_currency_name': iso_currency_name})
    except Exception as e:
        print('currencies', e)


async def prices():
    async with AsyncClient(TOKEN) as client:
        prices = await client.market_data.get_last_prices()
        temp = []
        rows = []
        for p in prices.last_prices:
            temp.append({'uid': p.instrument_uid, 'price': quotation_to_decimal(p.price), 'time': p.time})
            rows.append(Prices(uid=p.instrument_uid, price=quotation_to_decimal(p.price)))
        add_prices(rows)
        price = pd.DataFrame(temp)
        return price
