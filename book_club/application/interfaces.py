from abc import abstractmethod
from typing import Protocol
from uuid import UUID

from book_club.domain.entities import BookDM


class BookSaver(Protocol):
    @abstractmethod
    async def save(self, book: BookDM) -> None: ...


class BookReader(Protocol):
    @abstractmethod
    async def read_by_uuid(self, uuid: str) -> BookDM | None: ...


class UUIDGenerator(Protocol):
    def __call__(self) -> UUID: ...


class DBSession(Protocol):
    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def flush(self) -> None: ...
