import contextvars
import logging
from functools import wraps
from uuid import uuid4

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker

from app.base import Base
from app.config import config

session_context = contextvars.ContextVar("session_context")
engine = None
Session = None


def init_db():
    global engine, Session

    engine = create_async_engine(config.DB_URL, echo=True, future=True)
    session_factory = sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )
    Session = async_scoped_session(
        session_factory, scopefunc=lambda: session_context.get()
    )
    logging.info("Database engine and session initialized")


async def init_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def dispose_db():
    if engine:
        await engine.dispose()
        logging.info("Database engine disposed")


async def get_db_session():
    """
    요청마다 세션 생성 및 반환
    :return:
    """

    if Session is None:
        raise RuntimeError("Session is not initialized")

    token = session_context.set(str(uuid4()))
    async with Session() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            session_context.reset(token)


class Transactional:
    def __call__(self, func):
        @wraps(func)
        async def _transactional(*args, **kwargs):
            session = Session()

            if session is None:
                raise RuntimeError("No database session found for the current request.")

            try:
                result = await func(*args, **kwargs)
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e

            return result

        return _transactional
