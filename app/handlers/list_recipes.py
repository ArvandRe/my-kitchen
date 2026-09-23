from html import escape

from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.formatting import format_recipe
from app.keyboards.categories import CATEGORIES, list_categories_keyboard
from app.keyboards.list_menu import list_menu_keyboard
from app.keyboards.recipes_list import recipes_list_keyboard
from app.states.list_states import ListStates
from app.storage.json_storage import RecipeStorage


def setup(storage: RecipeStorage) -> Router:
    router = Router()

    @router.message(Command("list"))
    async def cmd_list(message: Message, command: CommandObject):
        word = (command.args or "").strip()

        if not word:
            await message.answer("Как искать рецепты?", reply_markup=list_menu_keyboard())
            return

        if word.lower() in (category.lower() for category in CATEGORIES):
            recipes = await storage.filter_by_category(word)
            title = f"Рецепты категории «{word}»"
        else:
            recipes = await storage.filter_by_ingredient(word)
            title = f"Рецепты с ингредиентом «{word}»"

        if not recipes:
            await message.answer("Такие рецепты не найдены.")
            return

        await message.answer(title, reply_markup=recipes_list_keyboard(recipes))

    @router.callback_query(F.data == "list:all")
    async def show_all(callback: CallbackQuery):
        recipes = await storage.get_all()
        if not recipes:
            await callback.message.edit_text("Рецепты не найдены.")
        else:
            await callback.message.edit_text("Все рецепты", reply_markup=recipes_list_keyboard(recipes))
        await callback.answer()

    @router.callback_query(F.data == "list:categories")
    async def show_categories(callback: CallbackQuery):
        await callback.message.edit_text("Выберите категорию:", reply_markup=list_categories_keyboard())
        await callback.answer()

    @router.callback_query(F.data == "list:ingredient")
    async def ask_ingredient(callback: CallbackQuery, state: FSMContext):
        await state.set_state(ListStates.waiting_for_ingredient)
        await callback.message.edit_text("Введите ингредиент для поиска:")
        await callback.answer()

    @router.message(ListStates.waiting_for_ingredient, F.text)
    async def process_ingredient_query(message: Message, state: FSMContext):
        ingredient = message.text.strip()
        await state.clear()
        recipes = await storage.filter_by_ingredient(ingredient)
        if not recipes:
            await message.answer("Такие рецепты не найдены.")
            return
        await message.answer(
            f"Рецепты с ингредиентом «{escape(ingredient)}»",
            reply_markup=recipes_list_keyboard(recipes),
        )

    @router.callback_query(F.data.startswith("listcat:"))
    async def show_category_recipes(callback: CallbackQuery):
        category = callback.data.split(":", 1)[1]
        recipes = await storage.filter_by_category(category)
        if not recipes:
            await callback.message.edit_text("Рецепты не найдены.")
        else:
            await callback.message.edit_text(
                f"Рецепты категории «{category}»", reply_markup=recipes_list_keyboard(recipes)
            )
        await callback.answer()

    @router.callback_query(F.data.startswith("recipe:"))
    async def show_recipe(callback: CallbackQuery):
        recipe_id = int(callback.data.split(":", 1)[1])
        recipe = await storage.get_by_id(recipe_id)
        if recipe is None:
            await callback.answer("Рецепт не найден.", show_alert=True)
            return
        await callback.message.answer(format_recipe(recipe))
        await callback.answer()

    return router
