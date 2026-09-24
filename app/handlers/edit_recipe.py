from html import escape

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.formatting import format_recipe
from app.keyboards.categories import categories_keyboard
from app.keyboards.recipes_list import recipes_list_keyboard
from app.states.edit_states import EditRecipeStates
from app.storage.json_storage import RecipeStorage

KEEP_VALUE = "."
KEEP_HINT = f' (или отправьте "{KEEP_VALUE}", чтобы оставить как есть)'


def format_plain_list(items: list[str]) -> str:
    return "\n".join(escape(item) for item in items)


def setup(storage: RecipeStorage) -> Router:
    router = Router()

    @router.message(Command("edit"))
    async def cmd_edit(message: Message):
        recipes = await storage.get_all()
        if not recipes:
            await message.answer("Рецептов пока нет.")
            return
        await message.answer(
            "Выберите рецепт для редактирования:",
            reply_markup=recipes_list_keyboard(recipes, prefix="editrecipe"),
        )

    @router.callback_query(F.data.startswith("editrecipe:"))
    async def start_edit(callback: CallbackQuery, state: FSMContext):
        recipe_id = int(callback.data.split(":", 1)[1])
        recipe = await storage.get_by_id(recipe_id)
        if recipe is None:
            await callback.answer("Рецепт не найден.", show_alert=True)
            return
        await state.update_data(
            edit_id=recipe_id,
            current_name=recipe["name"],
            current_category=recipe["category"],
            current_ingredients=recipe["ingredients"],
            current_steps=recipe["steps"],
        )
        await state.set_state(EditRecipeStates.waiting_for_name)
        await callback.message.edit_text(f"<code>{escape(recipe['name'])}</code>")
        await callback.message.answer(f"Введите новое название рецепта{KEEP_HINT}:")
        await callback.answer()

    @router.message(EditRecipeStates.waiting_for_name, F.text)
    async def process_name(message: Message, state: FSMContext):
        text = message.text.strip()
        data = await state.get_data()
        name = data["current_name"] if text == KEEP_VALUE else text
        await state.update_data(name=name)
        await state.set_state(EditRecipeStates.waiting_for_category)
        await message.answer(f"<code>{escape(data['current_category'])}</code>")
        await message.answer("Выберите категорию:", reply_markup=categories_keyboard())

    @router.callback_query(EditRecipeStates.waiting_for_category, F.data.startswith("category:"))
    async def process_category(callback: CallbackQuery, state: FSMContext):
        category = callback.data.split(":", 1)[1]
        await state.update_data(category=category)
        await state.set_state(EditRecipeStates.waiting_for_ingredients)
        data = await state.get_data()
        await callback.message.edit_text(f"Категория: {category}")
        await callback.message.answer(f"<pre>{format_plain_list(data['current_ingredients'])}</pre>")
        await callback.message.answer(
            f"Введите новый список ингредиентов, каждый с новой строки{KEEP_HINT}:"
        )
        await callback.answer()

    @router.message(EditRecipeStates.waiting_for_ingredients, F.text)
    async def process_ingredients(message: Message, state: FSMContext):
        data = await state.get_data()
        text = message.text.strip()
        if text == KEEP_VALUE:
            ingredients = data["current_ingredients"]
        else:
            ingredients = [line.strip() for line in message.text.splitlines() if line.strip()]
            if not ingredients:
                await message.answer("Список ингредиентов не может быть пустым. Попробуйте снова:")
                return
        await state.update_data(ingredients=ingredients)
        await state.set_state(EditRecipeStates.waiting_for_steps)
        await message.answer(f"<pre>{format_plain_list(data['current_steps'])}</pre>")
        await message.answer(
            f"Введите новые этапы приготовления, каждый этап с новой строки{KEEP_HINT}:"
        )

    @router.message(EditRecipeStates.waiting_for_steps, F.text)
    async def process_steps(message: Message, state: FSMContext):
        data = await state.get_data()
        text = message.text.strip()
        if text == KEEP_VALUE:
            steps = data["current_steps"]
        else:
            steps = [line.strip() for line in message.text.splitlines() if line.strip()]
            if not steps:
                await message.answer("Список этапов не может быть пустым. Попробуйте снова:")
                return
        recipe = await storage.update(
            recipe_id=data["edit_id"],
            name=data["name"],
            category=data["category"],
            ingredients=data["ingredients"],
            steps=steps,
        )
        await state.clear()
        if recipe is None:
            await message.answer("Не удалось сохранить изменения: рецепт не найден.")
            return
        await message.answer("✅ Рецепт обновлён!\n\n" + format_recipe(recipe))

    return router
