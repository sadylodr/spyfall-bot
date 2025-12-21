from typing import Annotated

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.states.game_states import GameJoining
from bot.services.game_manager import GameManager, get_game_manager


GameManagerDep = Annotated[GameManager, get_game_manager] 

router = Router()

@router.message(Command("join"))
async def cmd_join(message: Message, state: FSMContext):
    await message.answer("Введите код игры (<i>Например A1B2</i>): ")
    await state.set_state(GameJoining.waiting_for_code)
    
@router.message(GameJoining.waiting_for_code, F.text)
async def process_code(message: Message, state: FSMContext, manager: GameManagerDep):
    code = message.text.upper() 
    await state.clear() 
    
    telegram_id = message.from_user.id
    username = message.from_user.username
    
    success = await manager.add_player_to_room(code, telegram_id, username)
    
    if success:
        await message.answer(
            f"✅ Вы успешно присоединились к комнате <i>{code}</i>.\n"
            f"Ожидайте, пока создатель начнет игру.",
            parse_mode="HTML"
        )
        
    else:
        room = await manager.get_room_by_code(code)
        
        if not room:
            error_message = f"❌ Комната с кодом <i>{code}</i> не найдена."
        elif room.status != 'WAITING':
            error_message = f"❌ Игра в комнате <i>{code}</i> уже началась."
        else:
             error_message = f"❌ Не удалось присоединиться к комнате <i>{code}</i>."
             
        await message.answer(error_message, parse_mode="HTML")