## Стек

- FastAPI + SQLAlchemy (async) + PostgreSQL
- Docker Compose

## Запуск

**1. Скопируй переменные окружения:**

```bash
cp .env.example .env
```

**2. Запусти контейнеры:**

```bash
docker compose up --build -d
```

**3. Примени миграции:**

```bash
docker compose exec web alembic upgrade head
```

## Тесты

```bash
docker compose exec web pytest
```
