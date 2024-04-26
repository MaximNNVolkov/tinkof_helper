import app_logger as log
from aiogram import types
import aiogram.utils.markdown as fmt
from aiogram.fsm.context import FSMContext
from fsm.fsm_base import StateBonds
from defs.classes import User

log = log.get_logger(__name__)


async def cmd_start(message: types.Message, state: FSMContext):
    u = User(message.from_user)
    log.info('кнопка старт. ' + u.info_user())
    await message.answer('Привет! Я бот, который поможет сравнить параметры облигаций. Для начала нажмите Меню.')
    await message.delete()

async def cmd_help(message: types.Message):
    u = User(message.from_user)
    log.info('кнопка хэлп ' + u.info_user())
    await message.answer(fmt.text(
        fmt.text('Бот помогает сравнить параметры облигаций.'),
        fmt.text('Для поиска бумаги необходимо выбрать ввести команду /bonds'),
        fmt.text(''),
        fmt.text('Обнаруженные ошибки и предложения по доработкам прошу направлять автору @MaximVolkov'),
        sep='\n'))
    await message.delete()


async def user_msg(message: types.Message, state: FSMContext):
    u = User(message.from_user)
    log.info('сообщение от пользователя' + u.info_user())
    await message.answer('user_msg')


async def bonds_yeld(message: types.Message, state: FSMContext):
    u = User(message.from_user)
    log.info(f'{u.info_user()} оценка бондов')
    await state.set_state(StateBonds.enter_ticker)
    await message.answer('Пришлите тикер облигации или ссылку на облигацию из приложения брокера.')
    await message.delete()
