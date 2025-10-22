from collections.abc import AsyncIterator

import pytest
from dishka import AsyncContainer
from faker import Faker
from fastapi import FastAPI
from dishka.integrations.fastapi import setup_dishka
from httpx import AsyncClient, ASGITransport
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from book_club.infrastructure.models import Book
from book_club.controllers.http import book_router


@pytest.fixture
async def http_app(container: AsyncContainer) -> FastAPI:
    app = FastAPI()
    app.include_router(router=book_router)
    setup_dishka(container, app)
    return app


@pytest.fixture
async def http_client(http_app: FastAPI) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=http_app),
        base_url="http://",
    ) as client:
        yield client


async def test_get_book(
    session: AsyncSession,
    http_client: AsyncClient,
    faker: Faker,
) -> None:
    uuid = faker.uuid4()
    title = faker.pystr(min_chars=3, max_chars=120)
    pages = faker.pyint()
    is_read = faker.pybool()

    await session.execute(
        insert(Book).values(uuid=uuid, title=title, pages=pages, is_read=is_read)
    )

    result = await http_client.get(f"/book/{uuid}")
    assert result.status_code == 200
    assert result.json()["title"] == title
    assert result.json()["pages"] == pages
    assert result.json()["is_read"] == is_read
