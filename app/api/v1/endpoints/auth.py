from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import AccessToken, Credentials, UserRead
from app.services.auth import (
    EmailAlreadyRegistered,
    InvalidCredentials,
    authenticate_user,
    register_user,
)

router = APIRouter()


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a user",
)
def register(
    credentials: Credentials, session: Annotated[Session, Depends(get_db)]
) -> UserRead:
    try:
        return register_user(session, str(credentials.email), credentials.password)
    except EmailAlreadyRegistered as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        ) from error


@router.post("/login", response_model=AccessToken, summary="Log in and get an access token")
def login(
    credentials: Credentials, session: Annotated[Session, Depends(get_db)]
) -> AccessToken:
    try:
        token = authenticate_user(session, str(credentials.email), credentials.password)
    except InvalidCredentials as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error
    return AccessToken(access_token=token)
