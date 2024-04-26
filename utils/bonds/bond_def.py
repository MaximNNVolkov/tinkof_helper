import app_logger as log
from tinkoff.invest.utils import quotation_to_decimal
from aiogram import types
from aiogram.fsm.context import FSMContext
from defs.classes import User
from defs.accounts import Accounts
from utils.bonds.bond import Bond
from utils.bonds.card_bond import CardBond


log = log.get_logger(__name__)


def get_ticker(text: str) -> str:
    log.info(f"Получен тикер, {text}")
    ac = Accounts()
    instruments = ac.get_instruments()
    if text.startswith('$'):
        if not(instruments[instruments['ticker'] == text[1:]].empty):
            return instruments[instruments['ticker'] == text[1:]].uid.iloc[0]
    elif text.startswith('https://'):
        text = text.split('?')[0]
        texts = text.split('/')
        for t in texts:
            if not(instruments[instruments['ticker'] == t].empty):
                return instruments[instruments['ticker'] == t].uid.iloc[0]
    return None

async def get_tickers(message: types.Message, state: FSMContext):
    u = User(message.from_user)
    log.info(f"Получен тикер бумаги, {u.info_user()}")
    uid = get_ticker(message.text)
    if uid is None:
        await message.answer("Тикер не найден")
        return await state.clear()
    ac = Accounts()
    print(uid)
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
    b.get_coupons()
    b.get_last_price()
    b.get_bonds_event()
    b.coupon_fix()
    card_bond = CardBond(b)
    await message.answer(card_bond.get_text(), disable_web_page_preview=True)
    await message.delete()
    await state.clear()
