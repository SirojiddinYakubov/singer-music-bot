from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from bot.models.common_model import User

async def detect_user_language(user: types.User, session: AsyncSession) -> User | None:
    db_user = await session.execute(select(User).where(User.id == user.id))
    return db_user.scalar_one_or_none()

async def set_user_language(user: types.User, lang_code: str, session: AsyncSession):
    db_user = await session.execute(select(User).where(User.id == user.id))
    db_user = db_user.scalar_one_or_none()
    if not db_user:
        db_user = User(
            id=user.id,
            full_name=user.full_name,
            username=user.username,
            lang_code=lang_code
        )
        session.add(db_user)
        await session.commit()
    else:
        db_user.lang_code = lang_code
        session.add(db_user)
        await session.commit()