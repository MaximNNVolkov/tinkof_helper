import app_logger as log
from tinkoff.invest.utils import quotation_to_decimal
from aiogram import types
from aiogram.fsm.context import FSMContext
from defs.classes import User
from defs.accounts import Accounts
from utils.bonds.bond import Bond
from utils.bonds.card_bond import CardBond


log = log.get_logger(__name__)


async def get_tickers(message: types.Message, state: FSMContext):
    u = User(message.from_user)
    log.info(f"Получен тикер бумаги, {u.info_user()}")
    ticker = message.text
    if ticker.startswith('$'):
        ticker = ticker[1:]
    ac = Accounts()
    instruments = ac.get_instruments(ticker=ticker)
    print(type(instruments))
    if str(type(instruments)) == "<class 'str'>":
        await message.answer(instruments)
        await message.answer('Введите правильный тикер')
    elif instruments.type.iloc[0] != 'bonds':
        await message.answer(f'Тикер {ticker} не является облигацией')
        await message.answer('Введите правильный тикер')
    else:
        instr = ac.get_bond_by_uid(uid=instruments.uid.iloc[0])
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
        b.coupon_fix()
        card_bond = CardBond(b)
        be = b.get_bonds_event()
        print(be)
        await message.answer(card_bond.get_text(), disable_web_page_preview=True)
        await message.delete()
        await state.clear()
