from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def list_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📋 Все рецепты", callback_data="list:all")
    builder.button(text="🍲 По категории", callback_data="list:categories")
    builder.button(text="🥕 По ингредиенту", callback_data="list:ingredient")
    builder.adjust(1)
    return builder.as_markup()
