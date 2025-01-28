import logging
import uuid
from datetime import timedelta

from fastapi import APIRouter, Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.depends import refresh_token_depends
from app.auth.exception import DuplicateEmailException, TokenException
from app.auth.schema import (
    AccessToken,
    AuthResponse,
    RefreshToken,
    RefreshTokenSessionData,
    RegisterDTO,
)
from app.auth.service import (
    authenticate,
    create_jwt_token,
    create_user,
    find_by_id,
    is_user_exists,
    password_hash,
)
from app.cache.repository import BaseCacheRepository, get_cache_repository
from app.cache.session_manager import SessionManager
from app.common.responses import ResponseEntity
from app.session import get_db_session

auth_router = APIRouter()


@auth_router.post("/login", response_model=AuthResponse)
async def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_db_session),
    cache_repository: BaseCacheRepository = Depends(get_cache_repository),
):
    """
    # User Login
    """
    email = form_data.username
    password = form_data.password

    user = await authenticate(session=session, email=email, password=password)

    access_token_data = AccessToken(
        sub=str(user.user_id), name=user.name, role=user.role
    )
    refresh_token_data = RefreshToken()

    access_token = await create_jwt_token(
        access_token_data.model_dump(), timedelta(minutes=1)
    )

    refresh_token = await create_jwt_token(
        refresh_token_data.model_dump(), timedelta(minutes=60 * 24 * 30)
    )

    session_data = RefreshTokenSessionData(
        sub=str(user.user_id),
        name=user.name,
        role=user.role,
        ip=request.client.host,
        device_id=str(uuid.uuid4()),
    )

    session_manager = SessionManager(cache_repository)
    await session_manager.create_session(refresh_token, session_data)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=30 * 24 * 60 * 60,
    )

    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        name=user.name,
        role=user.role,
    )


@auth_router.post("/logout", response_model=ResponseEntity)
async def logout(
    request: Request,
    response: Response,
    cache_repository: BaseCacheRepository = Depends(get_cache_repository),
):
    """
    # User Logout
    """
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise TokenException(message="Not Found")

    session_manager = SessionManager(cache_repository)

    token_data = await session_manager.get_refresh_token_data(refresh_token)
    if not token_data:
        raise TokenException()

    user_id = token_data.get("sub")
    await session_manager.delete_session(refresh_token, user_id)

    response.delete_cookie(key="refresh_token")
    return ResponseEntity.ok(message="Logout Successfully")


@auth_router.post("/refresh", response_model=AuthResponse)
async def refresh(
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_db_session),
    refresh_token: str = Depends(refresh_token_depends),
    cache_repository: BaseCacheRepository = Depends(get_cache_repository),
):
    """
    # Refresh Token Rotation
    """
    session_manager = SessionManager(cache_repository)
    token_data = await session_manager.get_refresh_token_data(refresh_token)

    if not token_data:
        raise TokenException("token is none")

    user_id = token_data.get("sub")

    if await session_manager.is_token_reused(refresh_token):
        logging.info(f"Token has been reused : {refresh_token}")
        raise TokenException()

    refresh_token_data = RefreshToken()
    new_refresh_token = await create_jwt_token(
        refresh_token_data.model_dump(),
        timedelta(minutes=30 * 24 * 60),
    )

    user = await find_by_id(session=session, user_id=user_id)
    if not user:
        raise TokenException("User not found")

    new_session_data = RefreshTokenSessionData(
        sub=str(user.user_id),
        name=user.name,
        role=user.role,
        ip=request.client.host,
        device_id=str(uuid.uuid4()),
    )

    await session_manager.create_session(new_refresh_token, new_session_data)
    await session_manager.delete_session(refresh_token, user_id)

    access_token_data = AccessToken(
        sub=str(user.user_id), name=user.name, role=user.role
    )
    new_access_token = await create_jwt_token(
        access_token_data.model_dump(), timedelta(minutes=1)
    )

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        max_age=30 * 24 * 60 * 60,
    )

    return AuthResponse(
        access_token=new_access_token,
        token_type="bearer",
        name=user.name,
        role=user.role,
    )


@auth_router.post("/register", response_model=ResponseEntity)
async def register(
    register_dto: RegisterDTO,
    session: AsyncSession = Depends(get_db_session),
):
    """
    # User Register
    """
    if await is_user_exists(session=session, email=register_dto.email):
        raise DuplicateEmailException()

    await create_user(session=session, register_dto=register_dto)

    return ResponseEntity.create()
