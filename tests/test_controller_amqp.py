from collections.abc import AsyncIterator

import dishka_faststream
import pytest
from dishka import AsyncContainer
from faker import Faker
from faststream import FastStream
from faststream.rabbit import RabbitBroker
from faststream.rabbit import TestRabbitBroker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from book_club.controllers.amqp import AMQPBookController
from book_club.infrastructure.models import Book


@pytest.fixture
async def broker() -> RabbitBroker:
    broker = RabbitBroker()
    broker.include_router(AMQPBookController)
    return broker


@pytest.fixture
async def amqp_app(broker: RabbitBroker, container: AsyncContainer) -> FastStream:
    app = FastStream(broker)
    dishka_faststream.setup_dishka(container, app, auto_inject=True)
    return app


@pytest.fixture
async def amqp_client(amqp_app: FastStream) -> AsyncIterator[RabbitBroker]:
    async with TestRabbitBroker(amqp_app.broker) as br:
        yield br


async def test_save_book(
    amqp_client: RabbitBroker, session: AsyncSession, faker: Faker
) -> None:
    title, pages, is_read = faker.name_nonbinary(), faker.pyint(), faker.pybool()
    await amqp_client.publish(
        {"title": title, "pages": pages, "is_read": is_read}, queue="create_book"
    )

    result = await session.execute(
        select(Book).where(
            Book.title == title, Book.pages == pages, Book.is_read == is_read
        )
    )
    rows = result.fetchall()
    assert len(rows) == 1
    book = rows[0][0]
    assert book.title == title
    assert book.pages == pages
    assert book.is_read == is_read
