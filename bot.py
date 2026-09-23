import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from app.commands import BOT_COMMANDS
from app.config import ADMIN, BOT_TOKEN, DATA_FILE
from app.handlers import add_recipe, list_recipes, start
from app.middlewares.access import AccessMiddleware
from app.storage.json_storage import RecipeStorage


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not set. Add it to a .env file (see .env.example).")

    if not ADMIN:
        logging.warning("ADMIN is empty — no one will be able to use the bot.")

    recipe_storage = RecipeStorage(DATA_FILE)

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    dp.message.outer_middleware(AccessMiddleware())
    dp.callback_query.outer_middleware(AccessMiddleware())

    dp.include_router(start.router)
    dp.include_router(add_recipe.setup(recipe_storage))
    dp.include_router(list_recipes.setup(recipe_storage))

    await bot.set_my_commands(
        [BotCommand(command=command, description=description) for command, description in BOT_COMMANDS]
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
