import dishka_faststream
from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from faststream import FastStream

from book_club.config import Config
from book_club.controllers.http import book_router
from book_club.controllers.amqp import AMQPBookController
from book_club.infrastructure.resources.broker import new_broker
from book_club.ioc import AppProvider

config = Config()
container = make_async_container(AppProvider(), context={Config: config})


def get_faststream_app() -> FastStream:
    broker = new_broker(config.rabbitmq)
    faststream_app = FastStream(broker)
    dishka_faststream.setup_dishka(container, faststream_app, auto_inject=True)
    broker.include_router(AMQPBookController)
    return faststream_app


def get_fastapi_app() -> FastAPI:
    fastapi_app = FastAPI(title="Book club")
    fastapi_app.include_router(book_router)

    setup_dishka(container, fastapi_app)

    return fastapi_app


def get_app():
    faststream_app = get_faststream_app()
    fastapi_app = get_fastapi_app()

    fastapi_app.add_event_handler("startup", faststream_app.broker.start)
    fastapi_app.add_event_handler("shutdown", faststream_app.broker.close)

    return fastapi_app
