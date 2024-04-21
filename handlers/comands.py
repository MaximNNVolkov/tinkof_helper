from aiogram import Router
from aiogram.filters import Command, StateFilter
from comands.comands import cmd_start, cmd_help, user_msg, bonds_yeld
from middlewares.base import ChatActionMiddleware


router = Router()


router.message.register(cmd_start, Command('start'))
router.message.register(cmd_help, Command('help'))
router.message.register(bonds_yeld, Command('bonds'))
router.message.register(user_msg)
router.message.middleware(ChatActionMiddleware())
