# FastAPI-Dishka-FastStream

[![License - MIT](https://img.shields.io/badge/license-MIT-202235.svg?logo=python&labelColor=202235&color=edb641&logoColor=edb641)](https://spdx.org/licenses/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009485.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![FastStream](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fag2ai%2Ffaststream%2Fmain%2Fdocs%2Fdocs%2Fassets%2Fimg%2Fshield.json)](https://faststream.ag2.ai)
[![Dishka](https://img.shields.io/badge/Dishka-1.4.2+-green)](https://github.com/reagento/dishka)

This project is an implementation of "Clean architecture" in combining:
- [FastAPI](https://github.com/fastapi/fastapi)
- [Dishka](https://github.com/reagento/dishka)
- [FastStream](https://github.com/ag2ai/faststream)

> ⚡ **Why FastAPI?**\
The original example application was built using the Litestar framework. However, as the framework evolved, it took a rather specific development direction, so we decided to rewrite the materials using FastAPI. As of today, it is the most optimal framework choice for working with HTTP.

## Architecture Overview

- [Пишем универсальный прототип бэкенд-приложения](https://habr.com/ru/companies/pt/articles/820171/)
- [Практическое тестирование приложений](https://habr.com/ru/articles/958014/)

## Quick Start

### Prerequisites
- Python 3.10+
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
alembic revision --autogenerate -m "First migration"
alembic upgrade head
```

Create RabbitMQ queues:
```shell
docker exec -it book-club-rabbitmq rabbitmqadmin -u $RABBITMQ_USER -p $RABBITMQ_PASS declare queue --name=create_book --durable=false
docker exec -it book-club-rabbitmq rabbitmqadmin -u $RABBITMQ_USER -p $RABBITMQ_PASS declare queue --name=book_statuses --durable=false
```

Check RabbitMQ queues:
```shell
docker exec -it book-club-rabbitmq rabbitmqadmin -u $RABBITMQ_USER -p $RABBITMQ_PASS queues list
```

### Run the project

Full Application HTTP + AMQP (Recommended for demo):
```shell
uvicorn --factory book_club.main:get_app --reload
```
_but you also can run HTTP API only or AMQP consumer only_

```shell
// HTTP API Only
uvicorn --factory book_club.main:get_fastapi_app --reload

// AMQP Consumer Only
faststream run --factory book_club.main:get_faststream_app --reload
```

### Usage Examples

```shell
// Create a Book via AMQP
docker exec -it book-club-rabbitmq rabbitmqadmin -u $RABBITMQ_USER -p $RABBITMQ_PASS publish message --routing-key 'create_book' --exchange 'amq.default' --payload '{"title": "The Brothers Karamazov", "pages": 928, "is_read": true}'

// Read uuid of created book
docker exec -it book-club-rabbitmq rabbitmqadmin -u $RABBITMQ_USER -p $RABBITMQ_PASS get messages --queue 'book_statuses' --count 10

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
