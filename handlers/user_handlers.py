from aiogram import Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot.parser.itproger_parser import ITProgerParser
from bot.keyboards.reply import main_keyboard, upgrade_keyboard
from bot.keyboards.inline import article_keyboard


# Глобальные переменные для хранения состояния
news_cache = []
current_articles = []
current_index = 0


async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    await message.answer(
        "🤖 Добро пожаловать в ITProger News Bot!\n\n"
        "Я могу показать вам последние новости с itproger.com\n"
        "Используйте кнопки ниже для навигации:",
        reply_markup=main_keyboard()
    )


async def cmd_help(message: types.Message):
    """Обработчик команды /help"""
    await message.answer(
        "📖 Доступные команды:\n"
        "/start - начать работу\n"
        "/help - помощь\n\n"
        "📋 Доступные функции:\n"
        "• 📰 Последние новости - загрузить свежие статьи\n"
        "• 🔍 Поиск статей - найти статьи по ключевым словам\n"
        "• 🔄 Обновить данные - обновить список новостей\n"
        "• 📄 Текущая статья - показать текущую статью"
    )


async def show_latest_news(message: types.Message):
    """Показать последние новости"""
    global news_cache, current_articles, current_index
    
    await message.answer("🔄 Загружаю последние новости с itproger.com...", reply_markup=upgrade_keyboard())
    
    try:
        parser = ITProgerParser()
        news = parser.get_news_list()
        
        if not news:
            await message.answer("❌ Не удалось загрузить новости. Попробуйте позже.")
            return
        
        news_cache = news
        current_articles = news.copy()
        current_index = 0
        
        # Показываем первую статью
        await show_article_message(message, 0)
            
    except Exception as e:
        await message.answer(f"❌ Произошла ошибка: {str(e)}")


async def show_article_message(message: types.Message, index: int):
    """Показать статью по индексу"""
    global current_articles, current_index
    
    if not current_articles or index >= len(current_articles):
        await message.answer("❌ Статья не найдена")
        return
    
    article = current_articles[index]
    current_index = index
    
    # Формируем сообщение
    text = f"**{article['title']}**\n\n"
    
    if article.get('date'):
        text += f"📅 {article['date']}\n"
    
    if article.get('views'):
        text += f"👁️ {article['views']} просмотров\n\n"
    
    if article.get('description'):
        # Обрезаем описание если слишком длинное
        description = article['description']
        if len(description) > 300:
            description = description[:300] + "..."
        text += f"{description}\n\n"
    
    text += f"[📖 Читать на сайте]({article['url']})"

    # Создаем клавиатуру
    keyboard = article_keyboard(article['url'], index, len(current_articles))
    
    try:
        # Пытаемся отправить с изображением
        if article.get('image_url') and article['image_url'].startswith('http'):
            await message.answer_photo(
                photo=article['image_url'],
                caption=text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        else:
            await message.answer(
                text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
    except Exception as e:
        # Если не удалось отправить с фото, отправляем без него
        await message.answer(
            text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )


async def show_full_article_content(call: types.CallbackQuery):
    """Показать полное содержимое статьи"""
    global current_articles
    
    index = int(call.data.split(':')[1])
    
    if index >= len(current_articles):
        await call.answer("❌ Статья не найдена")
        return
    
    article = current_articles[index]
    
    await call.answer("🔄 Загружаю полное содержимое...")
    
    parser = ITProgerParser()
    full_content = parser.get_article_content(article['url'])
    
    content_text = f"**{full_content['title']}**\n\n"
    
    if full_content['full_content']:
        # Обрезаем текст если слишком длинный
        content = full_content['full_content']
        if len(content) > 4000:
            content = content[:4000] + "\n\n... (текст обрезан, читайте полную версию на сайте)"
        
        content_text += content
    else:
        content_text += "📝 Полное содержимое скоро будет доступно!\n\n"
        content_text += f"[Читать на сайте]({article['url']})"
    
    try:
        await call.message.answer(
            content_text,
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
    except Exception as e:
        await call.message.answer(
            "❌ Не удалось загрузить полное содержимое статьи",
            parse_mode='Markdown'
        )


async def search_articles(message: types.Message):
    """Поиск статей"""
    await message.answer(
        "🔍 Введите ключевые слова для поиска в последних новостях:\n\n"
        "Например: Python, JavaScript, ИИ, игры и т.д."
    )


async def handle_search_query(message: types.Message):
    """Обработчик поискового запроса"""
    global news_cache, current_articles, current_index
    
    query = message.text.strip()
    
    if not query:
        await message.answer("❌ Пожалуйста, введите поисковый запрос")
        return
    
    if not news_cache:
        await message.answer("🔄 Сначала загружаю новости...")
        await show_latest_news(message)
        return
    
    await message.answer(f"🔍 Ищу статьи по запросу: '{query}'...")
    
    parser = ITProgerParser()
    filtered_articles = []
    
    # Простой поиск по заголовку и описанию
    for article in news_cache:
        if (query.lower() in article['title'].lower() or 
            query.lower() in article.get('description', '').lower()):
            filtered_articles.append(article)
    
    if not filtered_articles:
        await message.answer(f"❌ По запросу '{query}' ничего не найдено")
        return
    
    current_articles = filtered_articles
    current_index = 0
    await message.answer(f"✅ Найдено статей: {len(filtered_articles)}")
    await show_article_message(message, 0)


async def handle_callback(call: types.CallbackQuery):
    """Обработчик callback запросов"""
    global current_index
    
    if call.data.startswith('article:'):
        index = int(call.data.split(':')[1])
        await call.answer()
        await show_article_message(call.message, index)
        
    elif call.data.startswith('full_content:'):
        await show_full_article_content(call)
    
    await call.answer()


async def handle_upgrade_data(message: types.Message):
    """Обновление данных"""
    await show_latest_news(message)


async def show_current_article(message: types.Message):
    """Показать текущую статью"""
    global current_articles, current_index
    
    if not current_articles:
        await message.answer("❌ Нет загруженных статей. Используйте '📰 Последние новости'")
        return
    
    await show_article_message(message, current_index)


async def handle_unknown_message(message: types.Message):
    """Обработчик неизвестных сообщений"""
    await message.answer(
        "🤔 Я не понял ваше сообщение.\n\n"
        "Используйте кнопки ниже или команды:\n"
        "/start - начать работу\n"
        "/help - помощь"
    )


def register_user_handlers(dp: Dispatcher):
    """Регистрация всех обработчиков пользователя"""
    # Команды
    dp.message.register(cmd_start, Command(commands=["start"]))
    dp.message.register(cmd_help, Command(commands=["help"]))
    
    # Текстовые обработчики
    dp.message.register(show_latest_news, lambda message: message.text == "📰 Последние новости")
    dp.message.register(search_articles, lambda message: message.text == "🔍 Поиск статей")
    dp.message.register(handle_upgrade_data, lambda message: message.text == "🔄 Обновить данные")
    dp.message.register(show_current_article, lambda message: message.text == "📄 Текущая статья")
    
    # Поисковые запросы (все текстовые сообщения, которые не являются командами)
    dp.message.register(handle_search_query)
    
    # Callback обработчики
    dp.callback_query.register(handle_callback)
    
    # Обработчик неизвестных сообщений (должен быть последним)
    dp.message.register(handle_unknown_message)