import dishka_faststream
from dishka import make_async_container
from dishka.integrations import litestar as litestar_integration
from faststream import FastStream
from litestar import Litestar

from book_club.config import Config
from book_club.controllers.amqp import AMQPBookController
from book_club.controllers.http import HTTPBookController
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


def get_litestar_app() -> Litestar:
    litestar_app = Litestar(
        route_handlers=[HTTPBookController],
    )
    litestar_integration.setup_dishka(container, litestar_app)
    return litestar_app


def get_app():
    faststream_app = get_faststream_app()
    litestar_app = get_litestar_app()

    litestar_app.on_startup.append(faststream_app.broker.start)
    litestar_app.on_shutdown.append(faststream_app.broker.close)

    return litestar_app
