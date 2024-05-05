from datetime import datetime, timedelta
import app_logger as log
from database.db_start import Instruments, db_conn
import pandas as pd
from config_reader import config
from tinkoff.invest import Client
from tinkoff.invest.constants import INVEST_GRPC_API
from tinkoff.invest.exceptions import RequestError


log = log.get_logger(__name__)
TOKEN = config.tinkoff_token.get_secret_value()


class UpdateInstruments:

    def __init__(self, force_update=False):
        if self.actual_data() or force_update:
            self.delete()
            instruments = self.get_instruments()
            self.update_instruments(instruments)

    def update_instruments(self, instruments: pd.DataFrame):
        conn = db_conn()
        for i, r in enumerate(instruments.itertuples(index=False)):
            instr = Instruments(
                ticker=r.ticker,
                class_code=r.class_code,
                figi=r.figi,
                uid=r.uid,
                type=r.type,
                name=r.name)

            conn.add(instr)
        conn.commit()
        log.debug(f'insert {i}')
        conn.close()

    def delete(self):
        conn = db_conn()
        res = conn.query(Instruments).delete()
        log.debug(f'deleted rows: {res}')
        conn.commit()
        conn.close()

    def actual_data(self):
        conn = db_conn()
        last_date = conn.query(Instruments).order_by(Instruments.date.desc()).first()
        if last_date is None:
            log.debug(f'last_date {last_date}')
            return True
        log.debug(f'last_date {last_date.date}')
        return last_date.date.date() < datetime.now().date()

    def get_uid(self, ticker: str) -> str:
        conn = db_conn()
        row = conn.query(Instruments).filter(Instruments.ticker == ticker).first()
        if row is None:
            return None
        uid = row.uid
        return uid

    def get_instruments(self):
        with Client(TOKEN, target=INVEST_GRPC_API) as client:
            instruments: InstrumentsService = client.instruments
            l = []
            for method in ['bonds']: #, 'etfs' ,'shares', 'currencies', 'futures']:
                log.info(f'получение списка бумаг {method}')
                try:
                    for item in getattr(instruments, method)().instruments:
                        l.append({
                            'ticker': item.ticker,
                            'class_code': item.class_code,
                            'figi': item.figi,
                            'uid': item.uid,
                            'type': method,
                            'name': item.name
                        })
                except RequestError:
                    log.error(RequestError.__dict__)
                else:
                    log.info(f'получено {len(l)} бумаг {method}')
            df = pd.DataFrame(l)
            if df.empty:
                return f"Нет тикера"
            return df
