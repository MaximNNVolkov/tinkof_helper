import app_logger as loger
from .db_start import db_conn, Users
import time


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
