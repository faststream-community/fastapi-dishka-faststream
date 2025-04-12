from typing import Annotated
from uuid import UUID
from http import HTTPStatus

from dishka.integrations.base import FromDishka as Depends
from dishka.integrations.litestar import inject
from litestar import Controller, route, HttpMethod
from litestar.exceptions import HTTPException
from litestar.params import Body

from book_club.application.interactors import GetBookInteractor
from book_club.controllers.schemas import BookSchema


class HTTPBookController(Controller):
    path = "/book"

    @route(http_method=HttpMethod.GET, path="/{book_id:uuid}")
    @inject
    async def get_book(
        self,
        book_id: Annotated[UUID, Body(description="Book ID", title="Book ID")],
        interactor: Depends[GetBookInteractor],
    ) -> BookSchema:
        book_dm = await interactor(uuid=str(book_id))
        if not book_dm:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail="Book not found"
            )
        return BookSchema(
            title=book_dm.title,
            pages=book_dm.pages,
            is_read=book_dm.is_read,
        )
