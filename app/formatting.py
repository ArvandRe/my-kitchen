from html import escape


def format_recipe(recipe: dict) -> str:
    ingredients = "\n".join(f"- {escape(i)}" for i in recipe["ingredients"])
    steps = "\n".join(f"{idx}. {escape(s)}" for idx, s in enumerate(recipe["steps"], start=1))
    return (
        f"<b>{escape(recipe['name'])}</b>\n"
        f"Категория: {escape(recipe['category'])}\n\n"
        f"<b>Ингредиенты:</b>\n{ingredients}\n\n"
        f"<b>Приготовление:</b>\n{steps}"
    )
