from typing import Union

from app.auth.schema import RefreshTokenSessionData
from app.cache.repository import BaseCacheRepository


class SessionManager:
    def __init__(self, cache_repository: BaseCacheRepository):
        self.cache_repository = cache_repository

    async def get_refresh_token_data(
        self, refresh_token: str
    ) -> Union[RefreshTokenSessionData, None]:
        key = f"refresh_token:{refresh_token}"
        token_data = await self.cache_repository.get(key)

        return token_data

    async def store_refresh_token_data(
        self, refresh_token: str, session_data: RefreshTokenSessionData
    ) -> None:
        key = f"refresh_token:{refresh_token}"
        await self.cache_repository.set(key, session_data.model_dump())

    async def store_user_session(
        self, user_id: str, device_id: str, refresh_token: str
    ) -> None:
        user_session_key = f"user_sessions:{user_id}:{device_id}"
        await self.cache_repository.set(user_session_key, refresh_token)

    async def invalidate_token(self, refresh_token: str) -> None:
        key = f"refresh_token:{refresh_token}"
        await self.cache_repository.delete(key)

    async def is_token_reused(self, refresh_token: str) -> bool:
        """
        Checks if a refresh token has been reused.
        """
        key = f"used_refresh_token:{refresh_token}"
        return await self.cache_repository.get(key) is not None

    async def mark_token_as_used(self, refresh_token: str) -> None:
        """
        Marks a refresh token as used to prevent reuse.
        """
        key = f"used_refresh_token:{refresh_token}"
        await self.cache_repository.set(key, "true")

    async def count_user_sessions(self, user_id: str) -> int:
        """
        Counts the number of active sessions for a given user.
        """
        pattern = f"user_sessions:{user_id}:*"
        keys = await self.cache_repository.scan(pattern)
        return len(keys)

    async def create_session(self, token: str, session_data: RefreshTokenSessionData):
        user_id = session_data.sub
        device_id = session_data.device_id

        await self.store_refresh_token_data(token, session_data)
        await self.store_user_session(user_id, device_id, token)

    async def delete_session(self, token: str, user_id: str):
        previous_key = f"refresh_token:{token}"
        await self.mark_token_as_used(token)
        await self.cache_repository.delete(previous_key)
        previous_user_session_key = f"user_session:{user_id}:{previous_key}"
        await self.cache_repository.delete(previous_user_session_key)
