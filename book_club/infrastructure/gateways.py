from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from book_club.application.interfaces import BookReader, BookSaver
from book_club.domain.entities import BookDM


class BookGateway(
    BookReader,
    BookSaver,
):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def read_by_uuid(self, uuid: str) -> BookDM | None:
        query = text("SELECT * FROM books WHERE uuid = :uuid")
        result = await self._session.execute(
            statement=query,
            params={"uuid": uuid},
        )
        row = result.fetchone()
        if not row:
            return None
        return BookDM(
            uuid=row.uuid,
            title=row.title,
            pages=row.pages,
            is_read=row.is_read,
        )

    async def save(self, book: BookDM) -> None:
        query = text(
            "INSERT INTO books (uuid, title, pages, is_read) VALUES (:uuid, :title, :pages, :is_read)"
        )
        await self._session.execute(
            statement=query,
            params={
                "uuid": book.uuid,
                "title": book.title,
                "pages": book.pages,
                "is_read": book.is_read,
            },
        )
