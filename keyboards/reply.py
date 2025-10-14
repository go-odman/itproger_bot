from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_keyboard():
    """Основная клавиатура"""
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📰 Последние новости")],
            [KeyboardButton(text="🔍 Поиск статей")],
            [KeyboardButton(text="🔄 Обновить данные")]
        ],
        resize_keyboard=True
    )
    return kb

def upgrade_keyboard():
    """Клавиатура с кнопкой обновления"""
    upgradeKB = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔄 Обновить данные")],
            [KeyboardButton(text="📰 Последние новости")],
            [KeyboardButton(text="🔍 Поиск статей")]
        ],
        resize_keyboard=True
    )
    return upgradeKB