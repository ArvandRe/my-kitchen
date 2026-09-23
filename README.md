# my-kitchen

Telegram-бот для хранения кулинарных рецептов, написанный на Python с использованием [aiogram](https://docs.aiogram.dev/) 3.x. Рецепты хранятся в JSON-файле.

## Возможности

- Добавление рецепта (название, категория, список ингредиентов, этапы приготовления) через пошаговый диалог.
- Просмотр списка рецептов в виде кнопок — по нажатию открывается полный текст рецепта.
- Поиск рецептов по категории или по ингредиенту одной командой.
- Меню команд бота (кнопка «Меню» в Telegram).
- Доступ к боту только у аккаунтов из списка администраторов (`ADMIN` в `.env`).

## Команды

| Команда | Описание |
|---|---|
| `/start` | Список команд с описанием |
| `/add` | Добавить новый рецепт (название → категория → ингредиенты → этапы приготовления) |
| `/list` | Показать все добавленные рецепты |
| `/list <слово>` | Если слово совпадает с категорией — показать рецепты этой категории, иначе — рецепты с таким ингредиентом. Например: `/list суп`, `/list тыква` |
| `/cancel` | Отменить текущее добавление рецепта |

Категории рецептов: суп, горячее, салат, десерт, консервация, напиток, гарнир, завтрак.

## Установка и запуск

1. Создать бота через [@BotFather](https://t.me/BotFather) и получить токен.
2. Установить зависимости:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Скопировать `.env.example` в `.env` и указать токен и Telegram ID администраторов (узнать свой ID можно, например, у [@userinfobot](https://t.me/userinfobot)):
   ```bash
   cp .env.example .env
   ```
   ```
   BOT_TOKEN=ваш_токен
   ADMIN=123456789;987654321
   ```
   Только перечисленные через `;` ID получат доступ к боту; остальным будет приходить сообщение «Доступ запрещён.».
4. Запустить бота:
   ```bash
   python bot.py
   ```

## Запуск как сервис systemd

Чтобы бот запускался автоматически при старте сервера и перезапускался при падении, оформите его как systemd-сервис.

1. Убедитесь, что проект развёрнут по постоянному пути (например `/opt/my-kitchen`) и виртуальное окружение `.venv` создано и содержит зависимости (см. шаг 2 выше), а `.env` заполнен.

2. Создайте юнит-файл `/etc/systemd/system/my-kitchen-bot.service`:
   ```ini
   [Unit]
   Description=my-kitchen Telegram bot
   After=network-online.target
   Wants=network-online.target

   [Service]
   Type=simple
   User=agniya
   WorkingDirectory=/opt/my-kitchen
   EnvironmentFile=/opt/my-kitchen/.env
   ExecStart=/opt/my-kitchen/.venv/bin/python /opt/my-kitchen/bot.py
   Restart=on-failure
   RestartSec=5

   [Install]
   WantedBy=multi-user.target
   ```
   Замените `User` и пути `WorkingDirectory`/`EnvironmentFile`/`ExecStart` на актуальные для вашего сервера.

3. Примените и запустите сервис:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable --now my-kitchen-bot
   ```

4. Проверить состояние и логи:
   ```bash
   sudo systemctl status my-kitchen-bot
   journalctl -u my-kitchen-bot -f
   ```

5. После обновления кода — перезапустить сервис:
   ```bash
   sudo systemctl restart my-kitchen-bot
   ```

## Структура проекта

```
my-kitchen/
├── bot.py                     # точка входа, настройка бота и диспетчера
├── requirements.txt
├── .env.example
├── data/
│   └── recipes.json           # хранилище рецептов
└── app/
    ├── config.py               # переменные окружения, путь к файлу данных, список ADMIN
    ├── commands.py              # список команд бота (для меню и /start)
    ├── formatting.py            # рендер рецепта в текст с HTML-разметкой
    ├── middlewares/
    │   └── access.py            # проверка доступа: только ID из ADMIN
    ├── storage/
    │   └── json_storage.py      # чтение/запись recipes.json, поиск по категории/ингредиенту
    ├── states/
    │   ├── recipe_states.py     # состояния FSM для команды /add
    │   └── list_states.py       # состояние FSM для поиска по ингредиенту в /list
    ├── keyboards/
    │   ├── categories.py        # инлайн-клавиатуры выбора категории
    │   ├── list_menu.py         # инлайн-клавиатура меню /list
    │   └── recipes_list.py      # инлайн-клавиатура со списком рецептов
    └── handlers/
        ├── start.py             # обработчик /start
        ├── add_recipe.py        # обработчик /add, /cancel
        └── list_recipes.py      # обработчик /list и показа рецепта
```

## Формат хранения данных

Рецепты хранятся в `data/recipes.json` в виде списка объектов:

```json
[
  {
    "id": 1,
    "name": "Тыквенный суп",
    "category": "суп",
    "ingredients": ["тыква", "лук", "сливки"],
    "steps": ["Обжарить лук", "Добавить тыкву", "Варить и пюрировать"],
    "author_id": 123456789
  }
]
```
