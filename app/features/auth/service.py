from app.features.auth.hashing import verify_password, hash_password
from app.features.auth.repository import create_user, get_user_by_email
from app.features.user.models import User


async def signup_user(db, user_data):
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise Exception("Email already registered")

    new_user = User(
        email=user_data.email,
        password=hash_password(user_data.password),
        name=user_data.name,
        phone_number=user_data.phone_number,
    )
    return await create_user(db, new_user)


async def authenticate_user(db, email, password):
    user = await get_user_by_email(db, email)
    if not user or not verify_password(password, user.password):
        return None
    return user


# async def authenticate_user(db: AsyncSession, email: str, password: str):
#     try:
#         result = await db.execute(select(User).filter(User.email == email))
#         user = result.scalars().one()
#     except NoResultFound:
#         return None
#
#     if not verify_password(password, user.password):
#         return None
#     return user
