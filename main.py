import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from bot.misc.config import config
from bot.handlers.user import common
from bot.handlers.game import creator, joiner
from bot.services.content_loader import content_loader
from bot.services.game_manager import create_game_manager

from db.database import init_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")

async def main():
    bot = Bot(
        token=config.bot_token,
        default = DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )    
    )
    
    dp = Dispatcher()

    dp.include_router(common.router)
    dp.include_router(creator.router)
    dp.include_router(joiner.router)

    game_manager_instance = await create_game_manager() 
    dp.workflow_data['manager'] = game_manager_instance
    
    logging.info("Initializing database...")
    await init_db()
    
    logging.info("Loading game content (heroes/cards)...")
    await content_loader.load_content()

    logging.info("Starting bot...")
    polling_task = asyncio.create_task(
        dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    )
    
    try:
        await polling_task
    except asyncio.CancelledError:
        pass


if __name__ == "__main__":
    try:
        asyncio.run(main()) 
    except KeyboardInterrupt:
        logging.info("Bot execution terminated by user (Ctrl+C).")
    except (SystemExit, Exception):
        logging.info("Bot stopped due to an error or system exit.")

