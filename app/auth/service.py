import copy
import hashlib
import uuid
from datetime import datetime, timedelta

import jwt
from app.config import config
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.exception import IncorrectEmailOrPassword, NotFoundUser
from app.auth.model import User
from app.auth.schema import RegisterDTO
from app.session import Transactional


async def create_jwt_token(
    data: dict, expires_delta: timedelta = timedelta(minutes=15)
) -> str:
    to_encode = copy.deepcopy(data)

    expiration_time = datetime.now() + expires_delta
    expiration_timestamp = int(expiration_time.timestamp())

    to_encode.update({"exp": expiration_timestamp})
    encoded_jwt = jwt.encode(to_encode, config.SECRET, algorithm="HS256")

    return encoded_jwt


async def password_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


async def compare_passwords(input_password: str, hashed_password: str) -> bool:
    hashed_input_password = await password_hash(input_password)

    return hashed_input_password == hashed_password


async def authenticate(*, session: AsyncSession, email: str, password: str) -> User:
    user = await find_by_email(session=session, email=email)
    if not user:
        raise NotFoundUser()

    same = await compare_passwords(password, user.password)

    if not same:
        raise IncorrectEmailOrPassword()

    return user


async def find_by_email(*, session: AsyncSession, email: str) -> User | None:
    query = select(User).where(User.email == email)
    result = await session.execute(query)

    return result.scalars().first()


async def find_by_id(*, session: AsyncSession, user_id: uuid.UUID) -> User | None:
    query = select(User).where(User.user_id == user_id)
    result = await session.execute(query)

    return result.scalars().first()


async def is_user_exists(
    *,
    session: AsyncSession,
    email: str,
):
    user = await find_by_email(session=session, email=email)
    return bool(user)


def get_default_role() -> str:
    return "USER"


@Transactional()
async def create_user(*, session: AsyncSession, register_dto: RegisterDTO):
    new_user = User(
        name=register_dto.name,
        email=register_dto.email,
        password=await password_hash(register_dto.password),
        role=get_default_role(),
    )

    session.add(new_user)
