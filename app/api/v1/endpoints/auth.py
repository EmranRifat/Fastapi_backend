
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db

from app.models.user import User
from app.schemas.auth import (
    AccessToken,
    LoginData,
    LoginResponse,
    RegisterCredentials,
    LoginCredentials,
    RegisterResponse,
    UserRead,
)

from app.services.auth import (
    EmailAlreadyRegistered,
    InvalidCredentials,
    authenticate_user,
    register_user,
)

router = APIRouter()


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a user",
)
def register(
    credentials: RegisterCredentials,
    session: Annotated[Session, Depends(get_db)],
) -> RegisterResponse:
    try:
        user = register_user(
            session,
            credentials.name,
            str(credentials.email),
            credentials.password,
        )

        return RegisterResponse(
            message="User created successfully",
            user=user,
        )

    except EmailAlreadyRegistered as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        ) from error

    
# ///////////////////********* login endpoint ************/////////////////



@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Log in and get user information",
)
def login(
    credentials: LoginCredentials,
    session: Annotated[Session, Depends(get_db)],
) -> LoginResponse:

    try:
        token = authenticate_user(
            session,
            str(credentials.email),
            credentials.password,
        )

    except InvalidCredentials as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error

    user = session.query(User).filter(
        User.email == str(credentials.email)
    ).first()

    return LoginResponse(
        success=True,
        message="Login successful",
        data=LoginData(
            access_token=token,
            token_type="bearer",
            user=UserRead.model_validate(user),
        ),
    )

