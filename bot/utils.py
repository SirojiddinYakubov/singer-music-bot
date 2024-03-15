import aiohttp

from bot.core.config import settings

GET_FILE_URL = "https://api.telegram.org/bot{token}/getFile?file_id={file_id}"


async def get_file_path(file_id: str) -> dict:
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        async with session.get(
                GET_FILE_URL.format(token=settings.TOKEN_API, file_id=file_id)
        ) as response:
            try:
                resp_json = await response.json()
                return resp_json["result"]["file_path"]
            except Exception as e:
                print("Error: ", e)
                return {}
