from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from pwdlib import PasswordHash
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User
from app.repositories.user import UserRepository

password_hash = PasswordHash.recommended()


class EmailAlreadyRegistered(Exception):
    pass


class InvalidCredentials(Exception):
    pass


def register_user(session: Session, email: str, password: str) -> User:
    users = UserRepository(session)
    if users.get_by_email(email) is not None:
        raise EmailAlreadyRegistered

    user = User(email=email, hashed_password=password_hash.hash(password))
    session.add(user)
    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise EmailAlreadyRegistered from error
    session.refresh(user)
    return user


def authenticate_user(session: Session, email: str, password: str) -> str:
    user = UserRepository(session).get_by_email(email)
    if (
        user is None
        or not password_hash.verify(password, user.hashed_password)
        or not user.is_active
    ):
        raise InvalidCredentials

    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    return jwt.encode(
        {"sub": str(user.id), "exp": expires_at},
        settings.secret_key.get_secret_value(),
        algorithm="HS256",
    )


def decode_access_token(token: str) -> UUID:
    payload = jwt.decode(
        token,
        settings.secret_key.get_secret_value(),
        algorithms=["HS256"],
    )
    return UUID(payload["sub"])
