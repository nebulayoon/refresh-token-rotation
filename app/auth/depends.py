from typing import Annotated

import jwt
from fastapi import Cookie
from jwt import ExpiredSignatureError, InvalidTokenError

from app.auth.exception import TokenException, TokenInvalidException
from app.config import config


async def refresh_token_depends(refresh_token: Annotated[str | None, Cookie()] = None):
    token = await check_token(refresh_token)

    try:
        await decode_auth_token(token)
    except ExpiredSignatureError as e:
        raise TokenInvalidException("Invalid token") from e
    except InvalidTokenError as e:
        raise TokenInvalidException("Invalid token") from e
    except Exception as e:
        raise TokenException("Token not found") from e

    return token


async def check_token(token: str | None):
    if not token:
        raise await TokenException("Token not found")
    return token


async def decode_auth_token(token: str, secret: str = config.SECRET):
    return jwt.decode(token, secret, algorithms=["HS256"])
