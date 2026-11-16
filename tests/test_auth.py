import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.user import User
from app.services.auth import decode_access_token, password_hash

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        with TestSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def test_register_user(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "Person@Example.com", "password": "secure-password"},
    )

    assert response.status_code == 201
    assert response.json()["email"] == "person@example.com"
    assert "hashed_password" not in response.json()

    with TestSessionLocal() as session:
        user = session.query(User).one()
        assert password_hash.verify("secure-password", user.hashed_password)


def test_registration_rejects_duplicate_email(client: TestClient) -> None:
    payload = {"email": "person@example.com", "password": "secure-password"}

    assert client.post("/api/v1/auth/register", json=payload).status_code == 201
    response = client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 409


def test_login_returns_valid_bearer_token(client: TestClient) -> None:
    payload = {"email": "person@example.com", "password": "secure-password"}
    client.post("/api/v1/auth/register", json=payload)

    response = client.post("/api/v1/auth/login", json=payload)

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert decode_access_token(response.json()["access_token"])


def test_login_rejects_invalid_password(client: TestClient) -> None:
    client.post(
        "/api/v1/auth/register",
        json={"email": "person@example.com", "password": "secure-password"},
    )

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "person@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_credentials_require_valid_email_and_password_length(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "not-an-email", "password": "short"},
    )

    assert response.status_code == 422
