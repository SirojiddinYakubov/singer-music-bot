from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from bot.core.config import settings

engine = create_async_engine(url=str(settings.ASYNC_DATABASE_URI), echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)