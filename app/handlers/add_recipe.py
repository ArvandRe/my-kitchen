from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.formatting import format_recipe
from app.keyboards.categories import categories_keyboard
from app.states.recipe_states import AddRecipeStates
from app.storage.json_storage import RecipeStorage


def setup(storage: RecipeStorage) -> Router:
    router = Router()

    @router.message(Command("cancel"))
    async def cmd_cancel(message: Message, state: FSMContext):
        if await state.get_state() is None:
            await message.answer("Нечего отменять.")
            return
        await state.clear()
        await message.answer("Добавление рецепта отменено.")

    @router.message(Command("add"))
    async def cmd_add(message: Message, state: FSMContext):
        await state.set_state(AddRecipeStates.waiting_for_name)
        await message.answer("Введите название рецепта:")

    @router.message(AddRecipeStates.waiting_for_name, F.text)
    async def process_name(message: Message, state: FSMContext):
        await state.update_data(name=message.text.strip())
        await state.set_state(AddRecipeStates.waiting_for_category)
        await message.answer("Выберите категорию:", reply_markup=categories_keyboard())

    @router.callback_query(AddRecipeStates.waiting_for_category, F.data.startswith("category:"))
    async def process_category(callback: CallbackQuery, state: FSMContext):
        category = callback.data.split(":", 1)[1]
        await state.update_data(category=category)
        await state.set_state(AddRecipeStates.waiting_for_ingredients)
        await callback.message.edit_text(f"Категория: {category}")
        await callback.message.answer("Введите список ингредиентов, каждый с новой строки:")
        await callback.answer()

    @router.message(AddRecipeStates.waiting_for_ingredients, F.text)
    async def process_ingredients(message: Message, state: FSMContext):
        ingredients = [line.strip() for line in message.text.splitlines() if line.strip()]
        if not ingredients:
            await message.answer("Список ингредиентов не может быть пустым. Попробуйте снова:")
            return
        await state.update_data(ingredients=ingredients)
        await state.set_state(AddRecipeStates.waiting_for_steps)
        await message.answer("Введите этапы приготовления, каждый этап с новой строки:")

    @router.message(AddRecipeStates.waiting_for_steps, F.text)
    async def process_steps(message: Message, state: FSMContext):
        steps = [line.strip() for line in message.text.splitlines() if line.strip()]
        if not steps:
            await message.answer("Список этапов не может быть пустым. Попробуйте снова:")
            return
        data = await state.get_data()
        recipe = await storage.add(
            name=data["name"],
            category=data["category"],
            ingredients=data["ingredients"],
            steps=steps,
            author_id=message.from_user.id,
        )
        await state.clear()
        await message.answer("✅ Рецепт добавлен!\n\n" + format_recipe(recipe))

    return router
