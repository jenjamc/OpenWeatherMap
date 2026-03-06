# OpenWeatherMap Service

FastAPI service that fetches forecast data from OpenWeather, returns batched responses for multiple cities, caches responses on disk, logs fetch metadata in SQLite, and enforces Redis-backed rate limiting.

## Features

- Multi-city forecast endpoint with async concurrency (`asyncio.gather` + semaphore).
- Input validation with Pydantic (`days_forecast` from `1..5`).
- File cache for recent city forecasts (`data/*.json`).
- SQLite event history for cached fetches.
- Redis-backed per-IP rate limiting.
- Alembic migrations for DB schema changes.
- Async test suite with `pytest`, `pytest-asyncio`, and `pytest-httpx`.

## Tech Stack

- Python `3.13`
- FastAPI + Uvicorn/Gunicorn
- SQLAlchemy (async) + SQLite
- Alembic
- Redis
- Poetry
- Docker Compose

## API

Base prefix: `/weather`

- `GET /weather/health` - DB connectivity check.
- `GET /weather/info` - service name and version.
- `GET /weather/get-by-cities` - forecast for one or more cities.

### Example Request

```bash
curl --get "http://localhost:4000/weather/get-by-cities" \
  --data-urlencode "cities=Kyiv" \
  --data-urlencode "cities=London" \
  --data-urlencode "days_forecast=2"
```

### Docs (non-production)

- Swagger UI: `http://localhost:4000/weather/docs`
- OpenAPI JSON: `http://localhost:4000/weather/openapi.json`

## Environment Variables

Create `.env` from `.env.example`:

```bash
cp .env.example .env
```

Important values:

- `ENV=LOCAL`
- `DEBUG=True`
- `OPENWEATHER_API_KEY=<your_api_key>`
- `REDIS_URL=redis://redis:6379/1` (Docker default)

If you run without Docker and Redis is local on your machine, use:

- `REDIS_URL=redis://localhost:6379/1`

## Start Locally

### Option 1 (Recommended): Docker Compose

This starts both Redis and the API container.

```bash
docker compose up --build
```

Service URL:

- `http://localhost:4000`

The container entrypoint runs migrations automatically (`alembic upgrade head`) before starting Gunicorn.

### Option 2: Native (Poetry on host machine)

1. Install dependencies:

```bash
bin/poetry install
```

2. Build the project:

```bash
docker compose build
```

3. Create env vars from `.env.example` for your shell session:

4. Run migrations:

```bash
bin/alembic upgrade head
```

5. Start the app:

```bash
docker compose up
```

## Developer Commands

Run tests (Docker helper):

```bash
bin/test
```

Run pre-commit (Docker helper):

```bash
bin/pre-commit
```

## Project Structure

```text
src/
  api/             # FastAPI routers and dependencies
  clients/         # HTTP clients (OpenWeather wrapper)
  models/          # SQLAlchemy models
  schemas/         # Pydantic request/response schemas
  services/        # Business logic (fetch + cache + persistence)
  settings/        # App configuration, DB, Redis, logging
  migrations/      # Alembic migration scripts
  tests/           # API tests and fixtures
```

## Notes

- Cache TTL is controlled by `CACHE_TTL_MINUTES` (default: `5`).
- Rate limiting currently uses `RATE_LIMIT_REQUESTS` as the Redis key TTL (default `5`), effectively allowing one request per client IP per TTL window on this endpoint.
- Forecast horizon is capped at 5 days by schema validation.
