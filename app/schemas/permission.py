from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from app.utils.ulid import validate_ulid


class PermissionBase(BaseModel):
    name: str
    resource: str
    action: str
    description: Optional[str] = None


class PermissionCreate(PermissionBase):
    pass


class Permission(PermissionBase):
    id: str = Field(..., description="ULID of permission", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
    created_at: datetime

    class Config:
        from_attributes = True

    @field_validator('id')
    @classmethod
    def validate_ulid(cls, v):
        if not validate_ulid(v):
            raise ValueError('Invalid ULID format')
        return v
