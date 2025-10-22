from typing import Annotated
from uuid import UUID

from dishka.integrations.fastapi import FromDishka as Depends
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Body, HTTPException, Path, status

from book_club.application.interactors import GetBookInteractor
from book_club.controllers.schemas import BookSchema


book_router = APIRouter(prefix="/book")


@book_router.get("/{book_id:uuid}")
@inject
async def get_book(
    book_id: Annotated[UUID, Path(description="Book ID", title="Book ID")],
    interactor: Depends[GetBookInteractor],
) -> BookSchema:
    book_dm = await interactor(uuid=str(book_id))

    if not book_dm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    return BookSchema(
        title=book_dm.title,
        pages=book_dm.pages,
        is_read=book_dm.is_read,
    )
