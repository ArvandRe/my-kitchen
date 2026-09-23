from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()

COMMANDS_DESCRIPTION = (
    "Привет! Я бот для хранения кулинарных рецептов.\n\n"
    "Доступные команды:\n"
    "/start — список команд с описанием\n"
    "/add — добавить новый рецепт\n"
    "/list — открыть меню поиска рецептов (все / по категории / по ингредиенту)\n"
    "/list &lt;слово&gt; — сразу показать рецепты по категории или ингредиенту "
    "(например: /list суп или /list тыква)\n"
    "/cancel — отменить добавление рецепта"
)


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(COMMANDS_DESCRIPTION)
