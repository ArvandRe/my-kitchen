import asyncio
import json
import os
from typing import Optional


class RecipeStorage:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._lock = asyncio.Lock()
        if not os.path.exists(self.file_path):
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            self._write([])

    def _read(self) -> list[dict]:
        with open(self.file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, recipes: list[dict]) -> None:
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(recipes, f, ensure_ascii=False, indent=2)

    async def get_all(self) -> list[dict]:
        async with self._lock:
            return self._read()

    async def get_by_id(self, recipe_id: int) -> Optional[dict]:
        async with self._lock:
            recipes = self._read()
        for recipe in recipes:
            if recipe["id"] == recipe_id:
                return recipe
        return None

    async def add(
        self,
        name: str,
        category: str,
        ingredients: list[str],
        steps: list[str],
        author_id: int,
    ) -> dict:
        async with self._lock:
            recipes = self._read()
            new_id = max((r["id"] for r in recipes), default=0) + 1
            recipe = {
                "id": new_id,
                "name": name,
                "category": category,
                "ingredients": ingredients,
                "steps": steps,
                "author_id": author_id,
            }
            recipes.append(recipe)
            self._write(recipes)
            return recipe

    async def filter_by_ingredient(self, ingredient: str) -> list[dict]:
        recipes = await self.get_all()
        needle = ingredient.strip().lower()
        return [
            r for r in recipes
            if any(needle in ing.lower() for ing in r["ingredients"])
        ]

    async def filter_by_category(self, category: str) -> list[dict]:
        recipes = await self.get_all()
        needle = category.strip().lower()
        return [r for r in recipes if r["category"].lower() == needle]
