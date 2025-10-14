import asyncio
from bot.handlers.user_handlers import register_user_handlers
from loader import dp, bot

async def main():
    register_user_handlers(dp)
    
    print("Bot running!")
    # Указываем, что мы хотим получать сообщения и нажатия на кнопки
    await dp.start_polling(bot, skip_updates=True, allowed_updates=["message", "callback_query"])

if __name__ == "__main__":
    asyncio.run(main())