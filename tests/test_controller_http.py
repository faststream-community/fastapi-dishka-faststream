from collections.abc import AsyncIterator

import pytest
from dishka import AsyncContainer
from dishka.integrations import litestar as litestar_integration
from faker import Faker
from litestar import Litestar
from litestar.testing import AsyncTestClient
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from book_club.controllers.http import HTTPBookController
from book_club.infrastructure.models import Book


@pytest.fixture
async def http_app(container: AsyncContainer) -> Litestar:
    app = Litestar(
        route_handlers=[HTTPBookController],
    )
    litestar_integration.setup_dishka(container, app)
    return app


@pytest.fixture
async def http_client(http_app: Litestar) -> AsyncIterator[AsyncTestClient]:
    async with AsyncTestClient(app=http_app) as client:
        yield client


async def test_get_book(
    session: AsyncSession,
    http_client: AsyncTestClient,
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
