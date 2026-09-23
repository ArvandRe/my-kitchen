import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN = [
    int(user_id.strip())
    for user_id in os.getenv("ADMIN", "").split(";")
    if user_id.strip()
]

DATA_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "recipes.json",
)
