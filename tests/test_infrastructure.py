import pytest
from faker import Faker
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from book_club.domain.entities import BookDM
from book_club.infrastructure.gateways import BookGateway
from book_club.infrastructure.models import Book

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def book_gateway(session: AsyncSession) -> BookGateway:
    return BookGateway(session=session)


async def test_create_book(
    session: AsyncSession, book_gateway: BookGateway, faker: Faker
) -> None:
    uuid = faker.uuid4()
    title = faker.pystr()
    pages = faker.pyint()
    is_read = faker.pybool()
    await session.execute(
        insert(Book).values(uuid=uuid, title=title, pages=pages, is_read=is_read)
    )
    result = await book_gateway.read_by_uuid(uuid)
    assert result.title == title
    assert result.pages == pages
    assert result.is_read is is_read


async def test_save_book(
    session: AsyncSession, book_gateway: BookGateway, faker: Faker
) -> None:
    book_dm = BookDM(
        uuid=faker.uuid4(),
        title=faker.pystr(),
        pages=faker.pyint(),
        is_read=faker.pybool(),
    )
    await book_gateway.save(book_dm)

    result = await session.execute(select(Book).where(Book.uuid == book_dm.uuid))
    rows = result.fetchall()
    assert len(rows) == 1
    book = rows[0][0]
    assert book.title == book_dm.title
    assert book.pages == book_dm.pages
    assert book.is_read == book_dm.is_read
