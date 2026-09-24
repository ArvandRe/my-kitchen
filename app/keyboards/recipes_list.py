from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def recipes_list_keyboard(recipes: list[dict], prefix: str = "recipe") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for recipe in recipes:
        builder.button(text=recipe["name"], callback_data=f"{prefix}:{recipe['id']}")
    builder.adjust(1)
    return builder.as_markup()
