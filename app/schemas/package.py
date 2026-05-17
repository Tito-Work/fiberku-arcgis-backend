from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.utils.ulid import validate_ulid


class PackageBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    color: Optional[str] = None
    is_active: bool = True


class PackageCreate(PackageBase):
    pass


class PackageUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    color: Optional[str] = None
    is_active: Optional[bool] = None


class Package(PackageBase):
    id: str = Field(..., description="ULID of the package", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
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


class PackageCoverageBase(BaseModel):
    package_id: str
    coverage_id: str
    is_active: bool = True


class PackageCoverageCreate(PackageCoverageBase):
    pass


class PackageCoverageUpdate(BaseModel):
    package_id: Optional[str] = None
    coverage_id: Optional[str] = None
    is_active: Optional[bool] = None


class PackageCoverage(PackageCoverageBase):
    id: str = Field(..., description="ULID of the package coverage", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
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

    @field_validator('coverage_id')
    @classmethod
    def validate_coverage_ulid(cls, v):
        if v and not validate_ulid(v):
            raise ValueError('Invalid ULID format for coverage_id')
        return v


class PackageWithCoverages(Package):
    coverages: List[dict] = []  # Will be populated with coverage data
