import datetime

import app_logger as log
from database.db_start import Instruments, db_conn
import pandas as pd


log = log.get_logger(__name__)


class UpdateInstruments:

    def update_instruments(self, instruments: pd.DataFrame):
        conn = db_conn()
        for r in instruments.itertuples(index=False):
            instr = Instruments(
                ticker=r.ticker,
                class_code=r.class_code,
                figi=r.figi,
                uid=r.uid,
                type=r.type,
                name=r.name)

            conn.add(instr)
        conn.commit()
        res = conn.refresh(instr)
        log.debug(f'insert {res}')
        conn.close()
        return res

    def delete(self):
        conn = db_conn()
        res = conn.query(Instruments).delete()
        log.debug(f'deleted rows: {res}')
        conn.commit()
        conn.close()

    def actual_date(self):
        conn = db_conn()
        last_date = conn.query(Instruments).order_by(Instruments.date.desc()).first()
        if last_date is None:
            log.debug(f'last_date {last_date}')
            return datetime.date(1900, 1, 1)
        log.debug(f'last_date {last_date.date}')
        return last_date.date.date()

    def get_uid(self, ticker: str) -> str:
        return None
