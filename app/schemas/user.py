from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
from app.utils.ulid import validate_ulid
import re

def is_email_format(value: str) -> bool:
    return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value) is not None

class UserBase(BaseModel):
    email: str
    username: str
    full_name: Optional[str] = None
    is_active: bool = True

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v):
        if not is_email_format(v):
            raise ValueError("Invalid email format")
        return v


class UserCreate(UserBase):
    password: str
    full_name: Optional[str] = None
    role_id: Optional[str] = None


class UserUpdate(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role_id: Optional[str] = None

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v):
        if v is not None and not is_email_format(v):
            raise ValueError("Invalid email format")
        return v


class Role(BaseModel):
    id: str
    name: str
    description: str

class User(UserBase):
    id: str = Field(..., description="ULID of the user", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
    created_at: datetime
    updated_at: Optional[datetime] = None
    full_name: Optional[str] = None
    roles: list[Role] = []

    class Config:
        from_attributes = True

    @field_validator('id')
    @classmethod
    def validate_ulid(cls, v):
        if not validate_ulid(v):
            raise ValueError('Invalid ULID format')
        return v


class UserLogin(BaseModel):
    username: str
    password: str
    full_name: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
