from typing import Annotated, List

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, ReplyKeyboardRemove

from bot.states.game_states import GameCreation
from bot.keyboards.inline import (
    create_theme_keyboard,
    create_game_management_keyboard,
    create_creator_active_keyboard,
    ThemeCallback,
    GameActionCallback,
    CREATOR_ACTIVE_BUTTON_NEW,
    CREATOR_ACTIVE_BUTTON_CLOSE,
)
from bot.services.game_manager import GameManager, create_game_manager
from db.models.player import Player


router = Router()

def format_players_list(players: List[Player], creator_id: int) -> str:
    names = []
    
    for player in players:
        name = player.username or str(player.telegram_id)
        
        if not name:
            name = "anonymous"
            
        status = "👑 Создатель" if player.telegram_id == creator_id else "👤 Игрок"
        
        names.append(f"- {name} ({status})")
        
    return "\n".join(names)

async def send_room_info(bot: Bot, room_code: str, chat_id: int, manager: GameManager, players: List[Player], kb: InlineKeyboardMarkup):
    me = await bot.get_me()
    invite_link = f"https://t.me/{me.username}?start={room_code}"
    
    room = await manager.get_room_by_code(room_code)
    if not room: return
    
    players_list_str = format_players_list(players, room.creator_id)
    
    theme_name = "Dota 2" if room.theme == 'DOTA' else "Clash Royale"
    
    text = (
        f"✅ <b>Комната создана!</b> Код: <i><b>{room_code}</b></i>\n"
        f"Тема: <b>{theme_name}</b>\n\n"
        f"🔗 <b>Ссылка для подключения:</b>\n"
        f"{invite_link}\n\n"
        f"👥 <b>Игроки в комнате</b> ({len(players)}):\n"
        f"{players_list_str}"
    )
    
    await bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=kb,
        parse_mode="HTML"
    )


async def notify_players_roles(bot: Bot, manager: GameManager, room_code: str) -> None:
    players = await manager.get_room_players(room_code)
    for player in players:
        info = await manager.get_player_role_info(player.telegram_id, room_code)
        if info:
            role, display_info, theme = info

            if role == 'SPY':
                role_text = f"🚨 <b>ВАША РОЛЬ: ШПИОН</b> 🚨\nТема: <i>{theme}</i>"
            else:
                role_text = f"✅ <b>ВАША РОЛЬ: ИГРОК</b>\nЗагадано: <i>{display_info}</i>"

            try:
                await bot.send_message(player.telegram_id, role_text, parse_mode="HTML")
            except Exception:
                pass


async def start_game_and_notify(bot: Bot, manager: GameManager, room_code: str, min_players: int) -> bool:
    players = await manager.get_room_players(room_code)
    if len(players) < min_players:
        return False

    await manager.distribute_roles(room_code, min_players=min_players)
    await notify_players_roles(bot, manager, room_code)
    return True
    
@router.message(Command("newgame"))
async def cmd_new_game(message: Message, state: FSMContext):
    await message.answer(
        "Выберите тему игры: ",
        reply_markup=create_theme_keyboard()
    )
    
    await state.set_state(GameCreation.waiting_for_theme)
    
@router.callback_query(GameCreation.waiting_for_theme, ThemeCallback.filter())
async def cb_theme_selected(callback: CallbackQuery, callback_data: ThemeCallback, state: FSMContext, manager: GameManager, bot: Bot):
    await callback.answer("Тема принята. Создаю комнату...")
    await state.clear()
    
    theme = callback_data.theme
    
    try:
        room = await manager.create_new_room(
            creator_id=callback.from_user.id,
            theme=theme
        )
        
        room_code = room.room_code
        
        players = await manager.get_room_players(room_code)
        
        kb = create_game_management_keyboard(room_code, is_creator=True)
        
        await send_room_info(
            bot=bot,
            room_code=room_code,
            chat_id=callback.from_user.id,
            manager=manager,
            players=players,
            kb=kb
        )
        
        await callback.message.delete()
        
    except Exception as e:
        await callback.message.answer(f"Произошла ошибка при создании комнаты: {e}")
        
@router.callback_query(GameActionCallback.filter(F.action.in_(['start', 'refresh', 'finish'])))
async def cb_game_action(callback: CallbackQuery, callback_data: GameActionCallback, manager: GameManager, bot: Bot):
    room_code = callback_data.code
    action = callback_data.action
    
    room = await manager.get_room_by_code(room_code)
    if not room or room.status != 'WAITING':
        await callback.answer("Игра уже началась или комната не найдена.", show_alert=True)
        return
        
    players = await manager.get_room_players(room_code)
    
    if action == 'refresh':
        await callback.answer(f"Список обновлен. Игроков: {len(players)}", show_alert=False)
        
        is_creator = callback.from_user.id == room.creator_id
        kb = create_game_management_keyboard(room_code, is_creator)
        
        await callback.message.edit_text(
            text=callback.message.text.split("👥")[0] + "\n\n👥 <b>Игроки в комнате</b>:\n" + format_players_list(players, room.creator_id),
            reply_markup=kb,
            parse_mode="HTML"
        )
        
    elif action == 'start':
        if callback.from_user.id != room.creator_id:
            await callback.answer("Только создатель может начать игру!", show_alert=True)
            return

        MIN_PLAYERS = 3
        if len(players) < MIN_PLAYERS:
            await callback.answer(f"Нужно минимум {MIN_PLAYERS} игрока для старта!", show_alert=True)
            return
            
        await callback.answer("Распределяю роли...")

        try:
            started = await start_game_and_notify(bot, manager, room_code, MIN_PLAYERS)
            if not started:
                await callback.message.answer(
                    f"Нужно минимум {MIN_PLAYERS} игрока для старта!",
                    parse_mode="HTML"
                )
                return

            await callback.message.edit_text(
                f"🎉 <b>ИГРА НАЧАЛАСЬ!</b> 🎉\n"
                f"Комната <i>{room_code}</i>.\n"
                f"Всем игрокам отправлены их роли в личные сообщения.\n"
                f"Обсуждение началось!"
            )

            await bot.send_message(
                callback.from_user.id,
                "Управление игрой:",
                reply_markup=create_creator_active_keyboard()
            )

        except Exception as e:
            await callback.message.answer(f"Ошибка при распределении ролей: {e}", parse_mode="HTML")

    elif action == 'finish':
        if callback.from_user.id != room.creator_id:
            await callback.answer("Только создатель может завершить игру!", show_alert=True)
            return

        await manager.finish_game(room_code)
        await callback.message.edit_text(
            f"Игра в комнате <i>{room_code}</i> завершена.",
            parse_mode="HTML"
        )


@router.message(F.text == CREATOR_ACTIVE_BUTTON_NEW)
async def cmd_creator_new_game(message: Message, manager: GameManager, bot: Bot):
    room = await manager.get_active_room_by_creator(message.from_user.id)
    if not room:
        await message.answer("Активная игра не найдена.")
        return

    MIN_PLAYERS = 3
    try:
        restarted = await manager.restart_game(room.room_code, min_players=MIN_PLAYERS)
        if not restarted:
            await message.answer(f"Нужно минимум {MIN_PLAYERS} игрока для старта!", parse_mode="HTML")
            return

        await notify_players_roles(bot, manager, room.room_code)
        await message.answer("Новая игра началась!", reply_markup=create_creator_active_keyboard())
    except Exception as e:
        await message.answer(f"Ошибка при запуске новой игры: {e}", parse_mode="HTML")


@router.message(F.text == CREATOR_ACTIVE_BUTTON_CLOSE)
async def cmd_creator_close_room(message: Message, manager: GameManager):
    room = await manager.get_active_room_by_creator(message.from_user.id)
    if not room:
        await message.answer("Активная игра не найдена.")
        return

    await manager.finish_game(room.room_code)
    await message.answer("Комната закрыта. Игра завершена.", reply_markup=ReplyKeyboardRemove())
    