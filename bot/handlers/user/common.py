from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.services.game_manager import GameManager


router = Router()

@router.message(CommandStart())
async def handle_start(message: Message, state: FSMContext, manager: GameManager):
    parts = message.text.split(maxsplit=1)
    if len(parts) > 1:
        code = parts[1].strip().upper()
        if code:
            telegram_id = message.from_user.id
            username = message.from_user.username
            await state.clear()

            success = await manager.add_player_to_room(code, telegram_id, username)
            if success:
                await message.answer(
                    f"✅ Вы успешно присоединились к комнате <i>{code}</i>.\n"
                    "Ожидайте, пока создатель начнет игру.",
                    parse_mode="HTML"
                )
                return

            room = await manager.get_room_by_code(code)
            if not room:
                error_message = f"❌ Комната с кодом <i>{code}</i> не найдена."
            elif room.status != 'WAITING':
                error_message = f"❌ Игра в комнате <i>{code}</i> уже началась."
            else:
                error_message = f"❌ Не удалось присоединиться к комнате <i>{code}</i>."

            await message.answer(error_message, parse_mode="HTML")
            return

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
        "/newgame - Создать новую игру.\n"
        "/join - Присоединиться к игре."
    )
    
    await message.answer(help_text)