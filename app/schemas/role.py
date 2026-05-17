from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime
from app.utils.ulid import validate_ulid
from app.schemas.permission import Permission


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True


class RoleCreate(RoleBase):
    permission_ids: Optional[List[str]] = []


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    permission_ids: Optional[List[str]] = None


class Role(RoleBase):
    id: str = Field(..., description="ULID of role", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
    created_at: datetime
    updated_at: Optional[datetime] = None
    permissions: List[Permission] = []

    class Config:
        from_attributes = True

    @field_validator('id')
    @classmethod
    def validate_ulid(cls, v):
        if not validate_ulid(v):
            raise ValueError('Invalid ULID format')
        return v


class UserWithRoles(BaseModel):
    id: str = Field(..., description="ULID of user", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
    email: str
    username: str
    is_active: bool
    created_at: datetime
    roles: List[Role] = []

    class Config:
        from_attributes = True

    @field_validator('id')
    @classmethod
    def validate_ulid(cls, v):
        if not validate_ulid(v):
            raise ValueError('Invalid ULID format')
        return v
