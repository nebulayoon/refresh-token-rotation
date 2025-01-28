from abc import ABC, abstractmethod


class BaseCacheRepository(ABC):
    @abstractmethod
    async def get(self, key: str):
        pass

    @abstractmethod
    async def set(self, key: str, value: str):
        pass

    @abstractmethod
    async def delete(self, key: str):
        pass

    @abstractmethod
    async def scan(self, pattern: str) -> list:
        pass


class InMemoryCacheRepository(BaseCacheRepository):
    def __init__(self):
        self.store = {}

    async def get(self, key: str):
        return self.store.get(key)

    async def set(self, key: str, value: dict):
        self.store[key] = value

    async def delete(self, key: str):
        if key in self.store:
            del self.store[key]

    async def scan(self, pattern: str) -> list:
        import fnmatch

        return [key for key in self.store.keys() if fnmatch.fnmatch(key, pattern)]


repository: BaseCacheRepository = InMemoryCacheRepository()


def get_cache_repository() -> BaseCacheRepository:
    return repository
