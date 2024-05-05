from aiogram import Router
from aiogram import filters
from fsm.fsm_base import StateBonds
from utils.bonds.bond_def import get_tickers, all_tickers
from aiogram.filters import Command


router_bonds = Router()


router_bonds.message.register(get_tickers, filters.StateFilter(StateBonds.enter_ticker))
router_bonds.message.register(all_tickers, Command("all_test"))
