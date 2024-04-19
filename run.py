import asyncio
import logging
import sys

from aiogram import Bot
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from bot.core.conf import dp, bot
from bot.core.config import settings
from bot.core.middleware import register_middlewares


async def polling_main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    register_middlewares(dp)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(url=f"{settings.BASE_WEBHOOK_URL}{settings.WEBHOOK_PATH}",
                          secret_token=settings.WEBHOOK_SECRET)


def webhook_main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    dp.startup.register(on_startup)
    register_middlewares(dp)
    app = web.Application()

    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=settings.WEBHOOK_SECRET,
    )

    webhook_requests_handler.register(app, path=settings.WEBHOOK_PATH)

    setup_application(app, dp, bot=bot)

    web.run_app(app, host=settings.WEB_SERVER_HOST, port=settings.WEB_SERVER_PORT)


if __name__ == "__main__":
    asyncio.run(polling_main())
    # webhook_main()
