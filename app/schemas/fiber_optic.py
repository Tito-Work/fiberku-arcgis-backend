from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from app.utils.ulid import validate_ulid


class FiberOpticBase(BaseModel):
    segment_id: str
    operator_id: str
    location: Optional[str] = None  # WKT format
    is_active: bool = True


class FiberOpticCreate(FiberOpticBase):
    pass


class FiberOpticUpdate(BaseModel):
    segment_id: Optional[str] = None
    operator_id: Optional[str] = None
    location: Optional[str] = None
    is_active: Optional[bool] = None


class FiberOptic(FiberOpticBase):
    id: str = Field(..., description="ULID of the fiber optic", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    is_deleted: bool = False
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    deleted_by: Optional[str] = None

    class Config:
        from_attributes = True

    @field_validator('id')
    @classmethod
    def validate_ulid(cls, v):
        if not validate_ulid(v):
            raise ValueError('Invalid ULID format')
        return v

    @field_validator('segment_id')
    @classmethod
    def validate_segment_ulid(cls, v):
        if v and not validate_ulid(v):
            raise ValueError('Invalid ULID format for segment_id')
        return v

    @field_validator('operator_id')
    @classmethod
    def validate_operator_ulid(cls, v):
        if v and not validate_ulid(v):
            raise ValueError('Invalid ULID format for operator_id')
        return v


class FiberOpticWithDetails(FiberOptic):
    segment: Optional[dict] = None  # Will be populated with segment data
    operator: Optional[dict] = None  # Will be populated with operator data
