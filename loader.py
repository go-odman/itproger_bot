from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv
import os

# Загружаем переменные из .env файла
load_dotenv()

# Получаем переменные окружения с проверкой
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Если BOT_TOKEN не найден, попробуем прочитать из старого config.py
if not BOT_TOKEN:
    try:
        from data.config import BOT_TOKEN as OLD_BOT_TOKEN
        BOT_TOKEN = OLD_BOT_TOKEN
        print("⚠️  Используется токен из config.py. Рекомендуется перейти на .env файл")
    except ImportError:
        raise ValueError(
            "BOT_TOKEN не найден ни в .env файле, ни в data/config.py\n"
            "Создайте файл .env в корне проекта с содержимым:\n"
            "BOT_TOKEN=ваш_токен_бота_здесь\n"
            "ITPROGER_URL=https://itproger.com/news"
        )

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен")

print("✅ BOT_TOKEN успешно загружен")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()