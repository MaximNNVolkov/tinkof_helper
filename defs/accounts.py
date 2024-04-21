import app_logger as log
from tinkoff.invest import Client
from tinkoff.invest.constants import INVEST_GRPC_API
from tinkoff.invest.exceptions import RequestError
from tinkoff.invest import AccountStatus, InstrumentIdType
from collections import namedtuple
from config_reader import config
from pandas import DataFrame


log = log.get_logger(__name__)
TOKEN = config.tinkoff_token.get_secret_value()


class Accounts:

    def acc(self):
        with Client(TOKEN, target=INVEST_GRPC_API) as client:
            temp = []
            Account = namedtuple('Account', ['id', 'name', 'status'])
            accs = client.users.get_accounts()
            accs = accs.accounts
            for a in accs:
                status = 'Open'
                if a.status == AccountStatus.ACCOUNT_STATUS_CLOSED:
                    status = 'Closed'
                temp.append(Account(a.id, a.name, status))
            return temp

    def portfolio(self, account_id: str):
        with Client(TOKEN, target=INVEST_GRPC_API) as client:
            return client.operations.get_portfolio(account_id=account_id)

    def get_coupons(self, uid: str):
        with Client(TOKEN, target=INVEST_GRPC_API) as client:
            return client.instruments.get_bond_coupons(instrument_id=uid)

    def get_instrument(self, uid: str):
        with Client(TOKEN, target=INVEST_GRPC_API) as client:
            return client.instruments.get_instrument_by(id=uid,
                                                        id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_UID).instrument

    def get_bond_by_ticker(self, ticker: str, class_code: str):
        with Client(TOKEN, target=INVEST_GRPC_API) as client:
            return client.instruments.bond_by(id=ticker,
                                              id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_TICKER,
                                              class_code=class_code).instrument

    def get_bond_by_uid(self, uid: str):
        with Client(TOKEN, target=INVEST_GRPC_API) as client:
            return client.instruments.bond_by(id=uid, id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_UID).instrument

    def get_instruments(self, ticker: str):
        with Client(TOKEN, target=INVEST_GRPC_API) as client:
            instruments: InstrumentsService = client.instruments
            l = []
            for method in ['bonds', 'etfs']: # ,'shares', 'currencies', 'futures']:
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

            df = DataFrame(l)

            df = df[df['ticker'] == ticker]
            if df.empty:
                return f"Нет тикера {ticker}"
            return df
