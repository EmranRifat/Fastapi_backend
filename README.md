# Ecommerce Backend

A small FastAPI and PostgreSQL starter organized so API, domain services, repositories, and
database concerns can grow independently.

## Structure

```text
app/
  api/v1/              Versioned REST routes
  core/                Application settings
  db/                  SQLAlchemy base, engine, and request sessions
  migrations/          Alembic migration environment and revisions
  models/              SQLAlchemy persistence models
  repositories/        Database access, added with each feature
  schemas/             Request and response schemas
  services/            Business rules and use cases
  migrations/          Alembic migration environment and revisions
  main.py              FastAPI application
```

Keep route handlers focused on HTTP concerns. Put business rules in services, database queries
in repositories, and use Pydantic schemas to validate and serialize API data. Add database
constraints and indexes alongside feature models and manage schema changes with migrations
instead of calling `metadata.create_all()` at application startup.

## Run locally

1. Create and activate a virtual environment, then install the project:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -e ".[dev]"
   ```

2. Copy `.env.example` to `.env`.
3. Start PostgreSQL with `docker compose up -d db`.
4. Start the API with `uvicorn app.main:app --reload`.
5. Open `http://127.0.0.1:8000/docs`; the health endpoint is `GET /api/v1/health`.
6. Apply database migrations with `alembic upgrade head` before registering users.

The authentication endpoints are `POST /api/v1/auth/register` and `POST /api/v1/auth/login`.
Both accept JSON with `email` and `password`; login returns a short-lived JWT bearer token.
Send it on protected requests as `Authorization: Bearer <access_token>`.

The database URL can be overridden with `DATABASE_URL`. Set a long, random `SECRET_KEY` and
appropriate `ACCESS_TOKEN_EXPIRE_MINUTES` for your deployment. Do not commit `.env`; use a
managed secret or environment variables outside local development.

After defining SQLAlchemy models, create and apply schema migrations with
`alembic revision --autogenerate -m "describe schema change"` and `alembic upgrade head`.

## Tests and lint

```powershell
pytest
ruff check .
```
