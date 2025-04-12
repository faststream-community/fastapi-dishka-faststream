from unittest.mock import create_autospec, MagicMock
from uuid import uuid4

import pytest

from faker import Faker
from book_club.application import interfaces
from book_club.application.dto import NewBookDTO
from book_club.application.interactors import GetBookInteractor, NewBookInteractor
from book_club.domain import entities

pytestmark = pytest.mark.asyncio


@pytest.fixture
def get_book_interactor() -> GetBookInteractor:
    book_gateway = create_autospec(interfaces.BookReader)
    return GetBookInteractor(book_gateway)


@pytest.mark.parametrize("uuid", [str(uuid4()), str(uuid4())])
async def test_get_book(get_book_interactor: GetBookInteractor, uuid: str) -> None:
    await get_book_interactor(uuid=uuid)
    get_book_interactor._book_gateway.read_by_uuid.assert_awaited_once_with(uuid=uuid)


@pytest.fixture
def new_book_interactor(faker: Faker) -> NewBookInteractor:
    db_session = create_autospec(interfaces.DBSession)
    book_gateway = create_autospec(interfaces.BookSaver)
    uuid_generator = MagicMock(return_value=faker.uuid4())
    return NewBookInteractor(db_session, book_gateway, uuid_generator)


async def test_new_book_interactor(new_book_interactor: NewBookInteractor, faker: Faker) -> None:
    dto = NewBookDTO(
        title=faker.pystr(),
        pages=faker.pyint(),
        is_read=faker.pybool(),
    )
    result = await new_book_interactor(dto=dto)
    uuid = str(new_book_interactor._uuid_generator())
    new_book_interactor._book_gateway.save.assert_awaited_with(
        entities.BookDM(
            uuid=uuid,
            title=dto.title,
            pages=dto.pages,
            is_read=dto.is_read,
        )
    )
    new_book_interactor._db_session.commit.assert_awaited_once()
    assert result == uuid
