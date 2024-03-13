import logging
from typing import Any, Awaitable, Callable, Dict

from bot.core.babel import babel, ALLOWED_LANGUAGES
from aiogram import types
from aiogram import BaseMiddleware


# class GetAcceptLanguageMiddleware(BaseMiddleware):
#     async def on_process_message(self, message: types.Message, data: dict):
#         await self.set_lang(message.from_user.id)

#     async def on_process_callback_query(
#         self, callback: types.CallbackQuery, data: dict
#     ):
#         await self.set_lang(callback.from_user.id)

#     @classmethod
#     async def set_lang(cls, user_id: int):
        # try:
        #     user_data = await user_collection.find_one({'_id': user_id})
        #     if user_data and 'lang' in user_data:
        #         lang = user_data['lang']
        #     else:
        #         lang = ALLOWED_LANGUAGES[0]
        # except Exception as e:
        #     logging.error(str(e))
        #     lang = ALLOWED_LANGUAGES[0]

        # if lang not in ALLOWED_LANGUAGES:
        #     lang = ALLOWED_LANGUAGES[0]

        # babel.locale = lang

 


class GetAcceptLanguageMiddleware(BaseMiddleware):
    async def on_process_message(self, message: types.Message, data: dict):
        await self.set_lang(message.from_user.id)

    async def on_process_callback_query(
        self, callback: types.CallbackQuery, data: dict
    ):
        await self.set_lang(callback.from_user.id)

    async def __call__(
        self,
        handler: Callable[[types.Message, Dict[str, Any]], Awaitable[Any]],
        event: types.Message,
        data: Dict[str, Any],
    ) -> Any:
        babel.locale = "ru"
        print(32, babel.locale)
        return await handler(event, data)
