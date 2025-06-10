from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.features.auth.hashing import verify_password
from app.features.user.models import User
from sqlalchemy.exc import NoResultFound


async def authenticate_user(db: AsyncSession, email: str, password: str):
    try:
        result = await db.execute(select(User).filter(User.email == email))
        user = result.scalars().one()
    except NoResultFound:
        return None

    if not verify_password(password, user.password):
        return None
    return user
