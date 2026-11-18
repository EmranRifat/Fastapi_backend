from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict, Field


class RegisterCredentials(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8)




class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    is_active: bool
    created_at: datetime


class RegisterResponse(BaseModel):
    message: str
    user: UserRead


class AccessToken(BaseModel):
    access_token: str
    token_type: str = "bearer"



class LoginCredentials(BaseModel):
    email: EmailStr
    password: str
    
from pydantic import BaseModel


class LoginData(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


class LoginResponse(BaseModel):
    success: bool
    message: str
    data: LoginData
