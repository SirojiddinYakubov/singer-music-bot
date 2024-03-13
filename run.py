import asyncio
from bot.core.conf import bot, dp
from bot.handlers import main_handler

async def main():
    print("Бот запущен")
    
    dp.include_routers(main_handler.router)
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

    


if __name__ == "__main__":
    asyncio.run(main())