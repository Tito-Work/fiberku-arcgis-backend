from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from decimal import Decimal
from app.utils.ulid import validate_ulid


class CustomerBase(BaseModel):
    code: Optional[str] = None
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    subdistrict: Optional[str] = None
    postcode: Optional[str] = None
    address: Optional[str] = None
    location: Optional[str] = None  # WKT format
    package_id: Optional[str] = None
    price: Optional[Decimal] = None
    is_active: bool = True


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    subdistrict: Optional[str] = None
    postcode: Optional[str] = None
    address: Optional[str] = None
    location: Optional[str] = None
    package_id: Optional[str] = None
    price: Optional[Decimal] = None
    is_active: Optional[bool] = None


class Customer(CustomerBase):
    id: str = Field(..., description="ULID of the customer", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
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

    @field_validator('package_id')
    @classmethod
    def validate_package_ulid(cls, v):
        if v and not validate_ulid(v):
            raise ValueError('Invalid ULID format for package_id')
        return v
