from aiogram import Router
from aiogram import filters
from fsm.fsm_base import StateBonds
from defs.bonds import get_tickers


router_bonds = Router()


router_bonds.message.register(get_tickers, filters.StateFilter(StateBonds.enter_ticker))
