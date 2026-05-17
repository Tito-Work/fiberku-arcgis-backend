from pydantic import BaseModel, Field, field_validator, field_serializer
from typing import Optional, List, Any
from datetime import datetime
from app.utils.ulid import validate_ulid
from geoalchemy2.elements import WKBElement
from geoalchemy2.shape import to_shape


class CoverageBase(BaseModel):
    area: str
    current_customer: int = 0
    max_customer: int
    location: Optional[str] = None  # WKT format
    is_active: bool = True


class CoverageCreate(CoverageBase):
    pass


class CoverageUpdate(BaseModel):
    area: Optional[str] = None
    current_customer: Optional[int] = None
    max_customer: Optional[int] = None
    location: Optional[str] = None
    is_active: Optional[bool] = None


class Coverage(CoverageBase):
    id: str = Field(..., description="ULID of the coverage", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
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

    @field_validator('location', mode='before')
    @classmethod
    def validate_location(cls, value: Any) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, str):
            return value
        if isinstance(value, WKBElement):
            geom = to_shape(value)
            return geom.wkt
        return value

    @field_serializer('location')
    @classmethod
    def serialize_location(cls, value):
        if value is None:
            return None
        if isinstance(value, str):
            return value
        if isinstance(value, WKBElement):
            geom = to_shape(value)
            return geom.wkt
        return value


class CoverageWithPackages(Coverage):
    packages: List[dict] = []  # Will be populated with package data
