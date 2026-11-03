from apps.models.user import User
from apps.schemas.user import UserCreate
from apps.core.security import hash_password
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError


async def get_user(db: AsyncSession, user_id: int) -> User | None:
    result = await db.scalars(select(User).where(User.id == user_id))
    return result.one_or_none()


async def create_user(db: AsyncSession, data: UserCreate) -> User | None:
    """Create a user; None if the email is already taken.

    Relies on the unique index on email, so concurrent sign-ups with the same
    email cannot both succeed.
    """
    create_data = data.model_dump(exclude={"password"})
    user = User(
        **create_data,
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        return None
    await db.refresh(user)

    return user


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.scalars(select(User).where(User.email == email))
    return result.one_or_none()
