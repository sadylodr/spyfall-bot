import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from bot.misc.config import config
from bot.handlers.user import common


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")

async def main():
    bot = Bot(
        token=config.bot_token,
        default = DefaultBotProperties(
            parse_mode=ParseMode.MARKDOWN_V2
        )    
    )
    dp = Dispatcher()

    dp.include_router(common.router)

    logging.info("Starting bot...")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot stopped!")

