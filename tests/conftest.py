import os
from typing import Any, AsyncGenerator
from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest
from dishka import AnyOf, Provider, Scope, provide
from dishka import AsyncContainer, make_async_container
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from book_club.application import interfaces
from book_club.config import Config
from book_club.config import PostgresConfig
from book_club.infrastructure.models import Base
from book_club.ioc import AppProvider

pytestmark = pytest.mark.asyncio


@pytest.fixture(scope="session")
def postgres_config() -> PostgresConfig:
    return PostgresConfig(
        POSTGRES_USER=os.getenv("POSTGRES_USER"),
        POSTGRES_PASSWORD=os.getenv("POSTGRES_PASSWORD"),
        POSTGRES_HOST=os.getenv("POSTGRES_HOST"),
        POSTGRES_PORT=int(os.getenv("POSTGRES_PORT")),
        POSTGRES_DB=os.getenv("TEST_DB"),
    )


@pytest.fixture(scope="session")
async def session_maker(
    postgres_config: PostgresConfig,
) -> async_sessionmaker[AsyncSession]:
    database_uri = (
        "postgresql+psycopg://{login}:{password}@{host}:{port}/{database}".format(
            login=postgres_config.login,
            password=postgres_config.password,
            host=postgres_config.host,
            port=postgres_config.port,
            database=postgres_config.database,
        )
    )
    engine = create_async_engine(database_uri)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    return async_sessionmaker(
        bind=engine, class_=AsyncSession, autoflush=False, expire_on_commit=False
    )


@pytest.fixture
async def session(
    session_maker: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, Any]:
    async with session_maker() as session:
        session.commit = AsyncMock()
        yield session
        await session.rollback()


@pytest.fixture
def mock_provider(session: AsyncSession) -> Provider:
    class MockProvider(AppProvider):
        @provide(scope=Scope.REQUEST)
        async def get_session(self) -> AnyOf[AsyncSession, interfaces.DBSession]:
            return session

    return MockProvider()


@pytest.fixture
def container(mock_provider: Provider) -> AsyncContainer:
    return make_async_container(mock_provider, context={Config: MagicMock()})
