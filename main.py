import asyncio
import app_logger as log

from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.bot import DefaultBotProperties

from config_reader import config
from handlers import comands
from middlewares.base import ChatActionMiddleware
from utils.instruments.update_coupons import get_coupon_value

import aioschedule


Token = config.bot_token.get_secret_value()
logger = log.get_logger(__name__)


async def scheduler():
    aioschedule.every().day.at('2:43').do(get_coupon_value)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def main():
    logger.info('bot started')
    asyncio.create_task(scheduler())
    bot = Bot(token=Token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    dp.update.outer_middleware(ChatActionMiddleware())
    dp.include_routers(comands.router)
    await bot.set_my_commands([types.BotCommand(command="start", description="Перезапустить бота"),
                               types.BotCommand(command="help", description="Помощь"),
                               types.BotCommand(command="bonds", description="Оценка облигации"),
                               types.BotCommand(command="find_top_bonds", description="Поиск облигаций")
                               ])
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
