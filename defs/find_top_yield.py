import datetime
import app_logger as log
from aiogram import types
from aiogram.fsm.context import FSMContext
from utils.instruments.update_prices import currencyces, prices
from utils.bonds.bonds_yield import bonds_yield
from database.defs_base import get_bonds_yield
import pandas as pd
from utils.bonds.bond import Bond
from utils.bonds.card_bond import CardBond
from config_reader import UserParams


log = log.get_logger(__name__)


"""
Функция find_top_yield ищет наивысшую доходность за день.

Аргументы:
    message (types.Message): сообщение, которое содержит информацию о запросе пользователя
    state (FSMContext): состояние машины состояний, используемое для управления состоянием диалога

Возвращает:
    None: функция не возвращает никакого значения, она просто отправляет карточки с результатами поиска наивысшей доходности за день
"""
async def find_top_yield(message: types.Message, state: FSMContext):
    """
    Find the top yield of the day
    """
    log.info(f"Find the top yield")

    # Получаем курсы валют
    await currencyces()

    # Получаем цены на активы
    await prices()

    # Получаем доходность по облигациям
    await bonds_yield()

    # Получаем данные о доходности по облигациям
    bonds = get_bonds_yield()

    # Преобразуем данные в DataFrame
    bonds = pd.DataFrame([b.__dict__ for b in bonds])

    # Устанавливаем фильтры для DataFrame
    bonds = set_filters(bonds)

    # Сортируем DataFrame по столбцу 'annual_yield' в порядке убывания
    bonds.sort_values(by='annual_yield', inplace=True, ascending=False)

    # Отправляем карточки с результатами поиска наивысшей доходности за день
    await send_cards(message, state, bonds.iloc[0:UserParams().res_count])



async def send_cards(message: types.Message, state: FSMContext, cards: pd.DataFrame):
    """
    Send cards
    """
    log.info(f"Send cards")

    for r in cards.itertuples():
        cb = CardBond(r)
        await message.answer(cb.get_text_fixed_coupon(), disable_web_page_preview=True)


def set_filters(bonds: pd.DataFrame):
    """
    Set filters
    """
    log.info(f"Set filters")
    bonds = bonds[(bonds.oferta - datetime.datetime.now().date()) > datetime.timedelta(days=10)]
    bonds = bonds[bonds['annual_yield'] > 0]
    bonds = bonds[(bonds['days_to_maturity'] > 0) & (bonds['days_to_maturity'] <= 30)]
    # bonds = bonds[bonds['last_coupon_date'] >= bonds['maturity_date']]
    # bonds = bonds[bonds['annual_yield'] > UserParams().min_yield_diff]
    return bonds
