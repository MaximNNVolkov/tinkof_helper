from utils.instruments.update_coupons import get_coupon_value
import app_logger as log
from aiogram import types


log = log.get_logger(__name__)


async def dev_test(message: types.Message):
    log.info(f"Dev test: {message.text}")
    await message.answer(f"Coupon value: get_coupon_value()")
    await get_coupon_value()
