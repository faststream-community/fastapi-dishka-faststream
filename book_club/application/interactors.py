from book_club.application import interfaces
from book_club.application.dto import NewBookDTO
from book_club.domain import entities


class GetBookInteractor:
    def __init__(
        self,
        book_gateway: interfaces.BookReader,
    ) -> None:
        self._book_gateway = book_gateway

    async def __call__(self, uuid: str) -> entities.BookDM | None:
        return await self._book_gateway.read_by_uuid(uuid)


class NewBookInteractor:
    def __init__(
        self,
        db_session: interfaces.DBSession,
        book_gateway: interfaces.BookSaver,
        uuid_generator: interfaces.UUIDGenerator,
    ) -> None:
        self._db_session = db_session
        self._book_gateway = book_gateway
        self._uuid_generator = uuid_generator

    async def __call__(self, dto: NewBookDTO) -> str:
        uuid = str(self._uuid_generator())
        book = entities.BookDM(
            uuid=uuid, title=dto.title, pages=dto.pages, is_read=dto.is_read
        )

        await self._book_gateway.save(book)
        await self._db_session.commit()
        return uuid
