from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

CATEGORIES = [
    "суп",
    "горячее",
    "салат",
    "десерт",
    "консервация",
    "напиток",
    "гарнир",
    "завтрак",
]


def categories_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for category in CATEGORIES:
        builder.button(text=category.capitalize(), callback_data=f"category:{category}")
    builder.adjust(2)
    return builder.as_markup()


def list_categories_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for category in CATEGORIES:
        builder.button(text=category.capitalize(), callback_data=f"listcat:{category}")
    builder.adjust(2)
    return builder.as_markup()
