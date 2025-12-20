from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message


router = Router()

@router.message(Command("start"))
async def handle_start(message: Message):
    welcome_text = (
        "Привет\\! Я бот для игры в \\*Шпиона\\* по мотивам Dota 2 или Clash Royale\\.\n\n"
        "Чтобы начать игру, используй команду `/newgame`\\.\n\n"
        "Если тебе прислали код, просто отправь его мне или перейди по ссылке\\."
    )

    await message.answer(welcome_text)

@router.message(Command("help"))
async def handle_help(message: Message):
    help_text = (
        "❓ \\*\\*Как играть\\?\\*\\*\\n"
        "1\\. Один человек создает игру командой `/newgame`\\.\n"
        "2\\. Бот выдает ему код/ссылку для приглашения\\.\n"
        "3\\. Остальные игроки присоединяются\\.\n"
        "4\\. Создатель нажимает \\*Начать игру\\*\\.\n"
        "5\\. Бот рандомно распределяет роли:\n"
        "   \\- \\*\\*Обычные игроки\\*\\* получают одинакового Героя/Карту\\.\n"
        "   \\- \\*\\*Один Шпион\\*\\* не получает ничего, кроме темы\\.\n"
        "6\\. Ваша задача — вычислить Шпиона, задача Шпиона — догадаться, о чем речь\\.\n\n"
        "Доступные команды:\n"
        "\\/newgame \\- Создать новую игру\\."
    )
    
    await message.answer(help_text)