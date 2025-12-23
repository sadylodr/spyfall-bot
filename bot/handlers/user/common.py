from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message


router = Router()

@router.message(Command("start"))
async def handle_start(message: Message):
    welcome_text = (
        f"Привет, <b>{message.from_user.full_name}</b>! Я бот для игры в <b>Шпиона</b> по мотивам Dota 2 или Clash Royale.\n\n"
        "Для создания игры, используй команду /newgame.\n\n"
        "Если тебе прислали <i>код</i>, используй команду /join или перейди по ссылке."
    )

    await message.answer(welcome_text)

@router.message(Command("help"))
async def handle_help(message: Message):
    help_text = (
        "❓ <b>Как играть?</b>\n"
        "1. Один человек создает игру командой /newgame.\n"
        "2. Бот выдает ему код/ссылку для приглашения.\n"
        "3. Остальные игроки присоединяются.\n"
        "4. Создатель нажимает <b>Начать игру</b>.\n"
        "5. Бот рандомно распределяет роли:\n"
        "   - <i><b>Обычные игроки</b></i> получают одинакового Героя/Карту.\n"
        "   - <i><b>Один Шпион</b></i> не получает ничего, кроме роли.\n"
        "6. Ваша задача — вычислить Шпиона, задача Шпиона — догадаться, о чем речь.\n\n"
        "Доступные команды:\n"
        "/newgame - Создать новую игру."
        "/join - Присоединиться к игре."
    )
    
    await message.answer(help_text)