from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters.callback_data import CallbackData


class ThemeCallback(CallbackData, prefix="theme"):
    theme: str

class GameActionCallback(CallbackData, prefix="action"):
    code: str
    action: str

def create_theme_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text="⚔️ Dota 2",
                callback_data=ThemeCallback(theme='DOTA').pack()
            )
        ],
        [
            InlineKeyboardButton(
                text="🏰 Clash Royale",
                callback_data=ThemeCallback(theme='CR').pack()
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def create_game_management_keyboard(room_code: str, is_creator: bool) -> InlineKeyboardMarkup:
    buttons = []
    
    if is_creator:
        buttons.append([
            InlineKeyboardButton(
                text="▶️ Начать игру!",
                callback_data=GameActionCallback(code=room_code, action='start').pack()
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(
            text="🔄 Обновить список",
            callback_data=GameActionCallback(code=room_code, action='refresh').pack()
        ),
        InlineKeyboardButton(
            text="❌ Закрыть комнату",
            callback_data=GameActionCallback(code=room_code, action='finish').pack()
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)