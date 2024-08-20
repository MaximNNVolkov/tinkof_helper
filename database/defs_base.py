import app_logger as loger
from .db_start import db_conn, Users, Currencies, Prices, Coupons, Bonds, OfertaDates, BondsYield
import time
from utils.raises.db_raises import NoCoupons, NoPrice, NoCurrency, NoBonds, NoEvent, NoBondYields


log = loger.get_logger(__name__)
date_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
date = time.strftime('%Y-%m-%d', time.localtime())


def add_user(user):
    log.info(
        f'Запрос на добавление нового пользователя с '
        f'{user.id}, {user.first_name}, {user.last_name}, {user.username}.')

    u = Users(user_id=user.id,
              first_name=user.first_name,
              last_name=user.last_name,
              user_name=user.username)
    conn = db_conn()
    conn.add(u)
    conn.commit()


def user_check(user):
    log.info(f'Запрос на поиск пользователя {user.id}.')
    conn = db_conn()
    s = conn.query(Users.user_id).filter(Users.user_id == user.id).all()
    if len(s) > 0:
        res = 'ok_user'
    else:
        res = 'no_user'
    return res


def add_currency(currency):
    log.info(f'''Запрос на добавление новой валюты {currency['ticker']}.''')
    conn = db_conn()
    s = conn.query(Currencies).filter(
        Currencies.uid == currency['uid']).all()
    if len(s) > 0:
        row = conn.query(Currencies).filter(Currencies.uid == currency['uid']).update({'price': currency['price']})
        conn.commit()
        log.debug(f'''Результат изменения валюты {currency['ticker']} на {currency['price']}, обновлено строк {row}''')
    else:
        i = Currencies(uid=currency['uid'],
                       ticker=currency['ticker'],
                       price=currency['price'],
                       iso_currency_name=currency['iso_currency_name'],)
        conn.add(i)
        conn.commit()
        log.debug(f'''добавление новой валюты {currency['ticker']}''')


def get_currency(iso_currency_name: str):
    log.info(f'Запрос на получение валюты {iso_currency_name}')
    conn = db_conn()
    s = conn.query(Currencies).filter(Currencies.iso_currency_name == iso_currency_name).all()
    if len(s) > 0:
        res = s[0].price
    else:
        raise NoCurrency(message=f'Такой валюты не найдено', iso_currency_name=iso_currency_name)
    conn.close()
    return res


def add_prices(prices: list):
    log.info(f'Запрос на добавление цен {len(prices)}')
    conn = db_conn()
    conn.query(Prices).delete()
    conn.commit()
    for p in prices:
        conn.add(p)
    conn.commit()
    conn.close()


def get_price(uid: str):
    log.info(f'Запрос на получение цены {uid}')
    conn = db_conn()
    s = conn.query(Prices).filter(Prices.uid == uid).all()
    if len(s) > 0:
        res = s[0]
    else:
        raise NoPrice(message=f'Такой валюты не найден', uid=uid)
    return res


def get_bonds(conn):
    log.info(f'Запрос на получение облигаций')
    s = conn.query(Bonds).all()
    return s


def add_coupons(coupons: list):
    log.info(f'Запрос на добавление купонов {len(coupons)}')
    conn = db_conn()
    conn.query(Coupons).delete()
    conn.commit()
    for p in coupons:
        conn.add(p)
    conn.commit()
    conn.close()


def get_coupon(uid: str):
    log.info(f'Запрос на получение купона {uid}')
    conn = db_conn()
    s = conn.query(Coupons).filter(Coupons.uid == uid).all()
    if len(s) > 0:
        res = s[0]
    else:
        raise NoCoupons(message=f'Купон не найден', uid=uid)
    conn.close()
    return res


def add_bonds(bonds: list):
    log.info(f'Запрос на добавление облигации {len(bonds)}')
    conn = db_conn()
    conn.query(Bonds).delete()
    conn.commit()
    for p in bonds:
        conn.add(p)
    conn.commit()
    conn.close()


def get_bond(uid: str):
    log.info(f'Запрос на получение облигации {uid}')
    conn = db_conn()
    s = conn.query(Bonds).filter(Bonds.uid == uid).all()
    if len(s) > 0:
        res = s[0]
    else:
        raise NoBonds(message=f'Облигация не найдена', uid=uid)
    conn.close()
    return res


def add_offer_date(offer_date: list):
    log.info(f'Запрос на добавление даты оферты {len(offer_date)}')
    conn = db_conn()
    conn.query(OfertaDates).delete()
    conn.commit()
    for p in offer_date:
        conn.add(p)
    conn.commit()
    conn.close()


def get_offer_date(uid: str):
    conn = db_conn()
    s = conn.query(OfertaDates).filter(OfertaDates.uid == uid).all()
    if len(s) > 0:
        res = s[0]
    else:
        # raise NoEvent(message=f'Дата оферты не найдена', uid=uid)
        return None
    conn.close()
    return res


def add_bonds_yield(bonds_yield: list):
    log.info(f'Запрос на добавление доходности облигации {len(bonds_yield)}')
    conn = db_conn()
    conn.query(BondsYield).delete()
    conn.commit()
    for p in bonds_yield:
        conn.add(p)
    conn.commit()
    conn.close()


def get_bonds_yield(**filters):
    log.info(f'Запрос на получение доходности с фильтрами {filters}')
    conn = db_conn()
    s = conn.query(BondsYield).all()
    if len(s) > 0:
        res = s
    else:
        raise NoBondYields(message=f'Не загрузилось ни одной записи о доходности', filter=filter)
    conn.close()
    return res
