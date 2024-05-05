import app_logger as log
from tinkoff.invest.utils import quotation_to_decimal
from aiogram import types
from aiogram.fsm.context import FSMContext
from defs.classes import User
from defs.accounts import Accounts
from utils.bonds.bond import Bond
from utils.bonds.card_bond import CardBond
from utils.instruments.update_instruments import UpdateInstruments
from datetime import datetime

from database.db_start import db_conn, Instruments


log = log.get_logger(__name__)


def get_ticker(text: str) -> str:
    log.debug(f"Получен тикер, {text}")
    ui = UpdateInstruments()
    if text.startswith('$'):
        uid = ui.get_uid(ticker=text[1:])
        if not(uid is None):
            return uid
    elif text.startswith('https://'):
        text = ''.join([text, '?'])
        text = text.split('?')[0]
        texts = text.split('/')
        for t in texts:
            uid = ui.get_uid(ticker=t)
            if not(uid is None):
                return uid
    else:
        uid = ui.get_uid(ticker=text)
        if not(uid is None):
            return uid
    return None

async def get_tickers(message: types.Message, state: FSMContext):
    u = User(message.from_user)
    log.info(f"Получен тикер бумаги, {u.info_user()}")
    uid = get_ticker(message.text)
    if uid is None:
        await message.answer("Тикер не найден")
        return await state.clear()
    ac = Accounts()
    instr = ac.get_bond_by_uid(uid=uid)
    b = Bond(name=instr.name,
                 ticker=instr.ticker,
                 uid=instr.uid,
                 nominal=float(quotation_to_decimal(instr.nominal)),
                 initial_nominal=float(quotation_to_decimal(instr.initial_nominal)),
                 coupon_quantity_per_year=instr.coupon_quantity_per_year,
                 maturity_date=instr.maturity_date,
                 aci_value=float(quotation_to_decimal(instr.aci_value)),
                 floating_coupon_flag=instr.floating_coupon_flag,
                 amortization_flag=instr.amortization_flag,
                 risk_level=instr.risk_level)
    if b.maturity_date.year == 1970:
        b.maturity_date = datetime(year=2099, month=12, day=31)
    b.get_coupons()
    b.get_last_price()
    b.get_bonds_event()
    s, c = b.get_coupon_value()
    if s > 0:
        if b.floating_coupon_flag:
            b.coupon_floating(sum_coupons=s)
            cb = CardBond(bond=b)
            text = cb.get_text_floating_coupon()
        else:
            b.coupon_fixed(sum_coupons=s)
            cb = CardBond(bond=b)
            text = cb.get_text_fixed_coupon()
        await message.answer(text, disable_web_page_preview=True)
        log.debug(f"Карточка по бумаге {uid} отправлена пользователю {u.info_user()}")
    else:
        log.debug(f"Не удалось получить купоны по бумаге {b.ticker}")
        await message.answer(f"Не удалось получить купоны по бумаге {b.ticker}")
    await message.delete()
    await state.clear()


async def all_tickers(message: types.Message, state: FSMContext):
    u = User(message.from_user)
    log.info(f"Получена команда на перебор всех тикеров, {u.info_user()}")
    conn = db_conn()
    instrs = conn.query(Instruments).all()
    for instr in instrs:
        uid = get_ticker(instr.ticker)
        if uid is None:
            await message.answer("Тикер не найден")
            return await state.clear()
        ac = Accounts()
        instr = ac.get_bond_by_uid(uid=uid)
        b = Bond(name=instr.name,
                 ticker=instr.ticker,
                 uid=instr.uid,
                 nominal=float(quotation_to_decimal(instr.nominal)),
                 initial_nominal=float(quotation_to_decimal(instr.initial_nominal)),
                 coupon_quantity_per_year=instr.coupon_quantity_per_year,
                 maturity_date=instr.maturity_date,
                 aci_value=float(quotation_to_decimal(instr.aci_value)),
                 floating_coupon_flag=instr.floating_coupon_flag,
                 amortization_flag=instr.amortization_flag,
                 risk_level=instr.risk_level)
        if b.maturity_date.year == 1970:
            b.maturity_date = datetime(year=2099, month=12, day=31)
        b.get_coupons()
        b.get_last_price()
        b.get_bonds_event()
        s, c = b.get_coupon_value()
        if s > 0:
            if b.floating_coupon_flag:
                b.coupon_floating(sum_coupons=s)
                cb = CardBond(bond=b)
                text = cb.get_text_floating_coupon()
            else:
                b.coupon_fixed(sum_coupons=s)
                cb = CardBond(bond=b)
                text = cb.get_text_fixed_coupon()
        await message.answer(text, disable_web_page_preview=True)
        log.debug(f"Карточка по бумаге {uid, instr.ticker} отправлена пользователю {u.info_user()}")
