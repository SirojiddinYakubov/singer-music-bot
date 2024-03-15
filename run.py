import asyncio

from bot.core.conf import bot, dp
from bot.core.middleware import register_middlewares


async def main():
    print("Бот запущен")
    register_middlewares(dp)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
