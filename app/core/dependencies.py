from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import SessionFactory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionFactory() as session:
        yield session
