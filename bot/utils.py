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