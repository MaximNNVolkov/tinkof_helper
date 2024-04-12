import app_logger as log
from aiogram import types
from defs.classes import User
from aiogram.fsm.context import FSMContext


log = log.get_logger(__name__)


async def cmd_start(message: types.Message, state: FSMContext):
    u = User(message.from_user)
    log.info('кнопка старт. ' + u.info_user())
    await message.answer('start')


async def cmd_help(message: types.Message):
    u = User(message.from_user)
    log.info('кнопка хэлп ' + u.info_user())
    await message.answer('OK help')


async def user_msg(message: types.Message, state: FSMContext):
    u = User(message.from_user)
    log.info('сообщение от пользователя' + u.info_user())
    await message.answer('user_msg')

