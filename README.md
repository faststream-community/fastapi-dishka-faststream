# Litestar-Dishka-FastStream

[![License - MIT](https://img.shields.io/badge/license-MIT-202235.svg?logo=python&labelColor=202235&color=edb641&logoColor=edb641)](https://spdx.org/licenses/)
[![Litestar Project](https://img.shields.io/badge/Litestar%20Org-%E2%AD%90%20Litestar-202235.svg?logo=python&labelColor=202235&color=edb641&logoColor=edb641)](https://github.com/litestar-org/litestar)
[![FastStream](https://camo.githubusercontent.com/4bbf0095f52083ac1b693fdab68466f859b674aeef4bcb5c92fb0c087812dfc0/68747470733a2f2f696d672e736869656c64732e696f2f656e64706f696e743f75726c3d68747470732533412532462532467261772e67697468756275736572636f6e74656e742e636f6d25324661673261692532466661737473747265616d2532466d61696e253246646f6373253246646f6373253246617373657473253246696d67253246736869656c642e6a736f6e)](https://faststream.airt.ai/)
[![Dishka](https://img.shields.io/badge/Dishka-1.4.2+-green)](https://github.com/reagento/dishka)

This project is an implementation of "Clean architecture" in combining:
- [Litestar](https://github.com/litestar-org/litestar)
- [Dishka](https://github.com/reagento/dishka)
- [FastStream](https://github.com/ag2ai/faststream)

## Architecture Overview

- [Пишем универсальный прототип бэкенд-приложения](https://habr.com/ru/companies/pt/articles/820171/)

## Quick Start

### Prerequisites
- Python 3.8+
- Docker & Docker Compose

### Installation

Set up virtual environment and install dependencies:
```shell
python3 -m venv venv  # Edit .env if needed
source venv/bin/activate
pip install -r requirements.txt
```

Configure environment and start services:
```shell
cp .env.dist .env
docker compose up -d
export $(grep -v '^#' .env | xargs)  # This command can be useful in the next stages
```

Initialize database:
```shell
alembic upgrade head
```

Create RabbitMQ queues:
```shell
docker exec -it book-club-rabbitmq rabbitmqadmin -u $RABBITMQ_USER -p $RABBITMQ_PASS -V / declare queue name=create_book durable=false
docker exec -it book-club-rabbitmq rabbitmqadmin -u $RABBITMQ_USER -p $RABBITMQ_PASS -V / declare queue name=book_statuses durable=false
```

### Run the project

Full Application HTTP + AMQP (Recommended for demo):
```shell
uvicorn --factory book_club.main:get_app --reload
```
_but you also can run HTTP API only or AMQP consumer only_

```shell
// HTTP API Only
uvicorn --factory book_club.main:get_litestar_app --reload

// AMQP Consumer Only
faststream run --factory book_club.main:get_faststream_app --reload
```

### Usage Examples

```shell
// Create a Book via AMQP
docker exec -it book-club-rabbitmq rabbitmqadmin -u $RABBITMQ_USER -p $RABBITMQ_PASS \
publish exchange=amq.default routing_key=create_book payload='{"title": "The Brothers Karamazov", "pages": 928, "is_read": true}'

// Read uuid of created book
docker exec -it book-club-rabbitmq rabbitmqadmin -u $RABBITMQ_USER -p $RABBITMQ_PASS get queue=book_statuses count=10

// Get book info by http api
curl http://localhost:8000/book/{uuid}
```

### Testing

Create test database:
```shell
docker exec -it book-club-postgres psql -U $POSTGRES_USER -d $POSTGRES_DB -c "CREATE DATABASE test_db"
```

Run tests:
```shell
TEST_DB=test_db pytest tests/ --asyncio-mode=auto
```
