from faststream.rabbit import RabbitBroker
from faststream.security import SASLPlaintext

from book_club.config import RabbitMQConfig


def new_broker(rabbitmq_config: RabbitMQConfig) -> RabbitBroker:
    return RabbitBroker(
        host=rabbitmq_config.host,
        port=rabbitmq_config.port,
        security=SASLPlaintext(
            username=rabbitmq_config.login,
            password=rabbitmq_config.password,
        ),
        virtualhost="/",
    )
