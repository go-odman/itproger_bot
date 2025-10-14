from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def article_keyboard(article_url: str, current_index: int, total_articles: int):
    """Клавиатура для навигации по статьям"""
    
    # Создаем список для рядов кнопок
    keyboard = []
    
    # Кнопка для полного содержимого
    full_content_button = [InlineKeyboardButton(
        text="📖 Полное содержимое", 
        callback_data=f"full_content:{current_index}"
    )]
    keyboard.append(full_content_button)
    
    # Ряд для навигации (Предыдущая и Следующая)
    navigation_buttons = []
    
    if current_index > 0:
        navigation_buttons.append(InlineKeyboardButton(
            text="⬅️ Предыдущая", 
            callback_data=f"article:{current_index-1}"
        ))
    
    if current_index < total_articles - 1:
        navigation_buttons.append(InlineKeyboardButton(
            text="➡️ Следующая", 
            callback_data=f"article:{current_index+1}"
        ))
    
    # Добавляем ряд навигации, если есть кнопки
    if navigation_buttons:
        keyboard.append(navigation_buttons)
    
    # Создаем клавиатуру с обязательным параметром inline_keyboard
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def pagination_keyboard(current_page: int, total_pages: int):
    """Клавиатура для пагинации"""
    
    buttons = []
    
    if current_page > 1:
        buttons.append(InlineKeyboardButton(
            text="⬅️ Назад", 
            callback_data=f"page:{current_page-1}"
        ))
    
    buttons.append(InlineKeyboardButton(
        text=f"{current_page}/{total_pages}", 
        callback_data="current"
    ))
    
    if current_page < total_pages:
        buttons.append(InlineKeyboardButton(
            text="Вперед ➡️", 
            callback_data=f"page:{current_page+1}"
        ))
    
    # Создаем клавиатуру с обязательным параметром inline_keyboard
    return InlineKeyboardMarkup(inline_keyboard=[buttons])