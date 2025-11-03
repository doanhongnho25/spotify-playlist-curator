.PHONY: up down migrate seed fmt

up:
docker-compose up --build

down:
docker-compose down -v

migrate:
docker-compose run --rm api alembic upgrade head

seed:
docker-compose run --rm api python -m app.seeds.example

fmt:
docker-compose run --rm api ruff check --fix
