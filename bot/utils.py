import aiofiles
import aiohttp
from aiogram.utils.i18n import gettext as _
from bot.core.config import settings

GET_FILE_URL = "https://api.telegram.org/bot{token}/getFile?file_id={file_id}"
DOWNLOAD_FILE_URL = "https://api.telegram.org/file/bot{token}/{file_path}"


async def get_file_path(file_id: str) -> tuple[int, str]:
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        async with session.get(
                GET_FILE_URL.format(token=settings.TOKEN_API, file_id=file_id)
        ) as response:
            try:
                resp_json = await response.json()
                if "ok" in resp_json and not resp_json["ok"]:
                    return 400, resp_json['description']
                return 200, resp_json["result"]["file_path"]
            except Exception as e:
                print("Error: ", e)
                return 400, ""


async def download_audio(file_id: str, path: str) -> bool:
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        async with session.get(
                GET_FILE_URL.format(token=settings.TOKEN_API, file_id=file_id)
        ) as response:
            if response.status != 200:
                raise Exception(
                    _(
                        "Fayl yuklashda xatolik yuz berdi! {url} bo'yicha 200 status qabul qilinmadi!"
                    ).format(url=GET_FILE_URL)
                )
            res_json = await response.json()
            if "result" in res_json and "file_path" not in res_json["result"]:
                raise Exception(
                    _(
                        "Fayl yuklashda xatolik yuz berdi! {url} bo'yicha 'result' 'file_path' topilmadi!"
                    ).format(url=GET_FILE_URL)
                )
            file_path = res_json["result"]["file_path"]

            async with session.get(
                    DOWNLOAD_FILE_URL.format(
                        token=settings.TOKEN_API, file_path=file_path
                    )
            ) as response:
                if response.status != 200:
                    raise Exception(
                        _(
                            "Fayl yuklashda xatolik yuz berdi! {url} bo'yicha 200 status qabul qilinmadi!"
                        ).format(url=DOWNLOAD_FILE_URL)
                    )

                async with aiofiles.open(path, 'wb') as file:
                    async for data, t in response.content.iter_chunks():
                        await file.write(data)
            # with open(path, 'wb') as f:
            #     async for chunk in response.content.iter_chunked(10):
            #         f.write(chunk)
            # f = await aiofiles.open(path, mode='wb')
            # await f.write(await response.read())
            # await f.close()


async def handle_error(message: str, exc: Exception = None):
    from bot.core.conf import bot
    print("Error: ", exc)
    for admin_id in settings.ADMIN_IDS:
        await bot.send_message(admin_id, message)


def size_representation(size_bytes):
    """
    This function takes the size of music in bytes as input and returns the size in MB or KB.

    Args:
        size_bytes: The size of the music in bytes.

    Returns:
        A string representing the size of the music in MB or KB.
    """
    # Check if the size is greater than or equal to 1 MB
    if size_bytes >= 1048576:
        return f"{size_bytes / 1048576:.2f} MB"
    # Otherwise, return the size in KB
    else:
        return f"{size_bytes / 1024:.2f} KB"
