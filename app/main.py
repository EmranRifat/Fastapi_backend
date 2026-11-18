
from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings

from app.db.base import Base
from app.db.session import engine

# Import models before creating tables
from app.models.user import User

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
)


@app.on_event("startup")
def create_database_tables():
    Base.metadata.create_all(bind=engine)


app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/", include_in_schema=False)
def root() -> dict[str, str]:
    return {"message": f"{settings.app_name} API"}
