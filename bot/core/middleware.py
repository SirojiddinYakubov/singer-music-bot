from aiogram import Dispatcher
from aiogram.utils.i18n import I18n, ConstI18nMiddleware

i18n = I18n(path="bot/locales", default_locale="uz", domain="messages")
i18n_middleware = ConstI18nMiddleware(i18n=i18n, locale="ru")


def register_middlewares(dp: Dispatcher):
    dp.update.outer_middleware(i18n_middleware)
