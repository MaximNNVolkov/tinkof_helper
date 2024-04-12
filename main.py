import asyncio
import app_logger as log

from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.bot import DefaultBotProperties

from config_reader import config
from handlers import comands
from middlewares.base import ChatActionMiddleware


Token = config.bot_token.get_secret_value()
logger = log.get_logger(__name__)


async def main():
    logger.info('bot started')
    bot = Bot(token=Token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    dp.update.outer_middleware(ChatActionMiddleware())
    dp.include_routers(comands.router)
    await bot.set_my_commands([types.BotCommand(command="start", description="Перезапустить бота"),
                               types.BotCommand(command="help", description="Помощь")])
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
