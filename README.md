# SpyfallBot

Telegram bot to play Spyfall-style rounds themed around Dota 2 or Clash Royale.

## Requirements

- Python 3.11+
- A Telegram Bot token (from @BotFather)

## Setup (local)

1) Create and activate a virtual environment.
2) Install dependencies:

```
pip install -r requirements.txt
```

3) Create a `.env` file (see `.env.example`) and set `BOT_TOKEN`.
4) Run the bot:

```
python main.py
```

## Commands

- `/start` - Greeting and optional deep link join
- `/newgame` - Create a room
- `/join` - Join by code
- `/help` - Help text

## Notes

- Game data is loaded from `data/dota_heroes.json` and `data/clash_royale_cards.json`.
- The SQLite database is stored at `db/database.db`.
