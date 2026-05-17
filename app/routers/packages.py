from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.package import Package as PackageSchema, PackageCreate, PackageUpdate, PackageCoverage as PackageCoverageSchema, PackageCoverageCreate, PackageCoverageUpdate
from app.services.package_service import PackageService, PackageCoverageService
from app.middleware.rbac import get_current_user_with_permission
from app.models.user import User
from app.utils.ulid import validate_ulid
from app.schemas.base_response import BaseResponse
from app.exceptions.http_exception import AppException
from app.utils.logging_system import log_errors, api_logger

router = APIRouter()


# Package endpoints
@log_errors(api_logger)
@router.post("", response_model=BaseResponse[PackageSchema], status_code=status.HTTP_201_CREATED)
def create_package(
    package: PackageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("create_package"))
):
    package_service = PackageService(db)
    
    if package_service.get_package_by_name(package.name):
        raise AppException(
            status_code=400,
            code="400",
            message="Package already exists"
        )
    
    created_package = package_service.create_package(package, created_by=current_user.id)
    return {
        "status": True,
        "code": "10001",
        "message": "Package created successfully",
        "data": created_package
    }


@log_errors(api_logger)
@router.get("", response_model=BaseResponse[List[PackageSchema]])
def read_packages(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("read_package"))
):
    package_service = PackageService(db)
    packages = package_service.get_packages(skip=skip, limit=limit)
    return {
        "status": True,
        "code": "10002",
        "message": "Packages fetched successfully",
        "data": packages
    }


@log_errors(api_logger)
@router.get("/{package_id}", response_model=BaseResponse[PackageSchema])
def read_package(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("read_package")),
    package_id: str = Path(..., description="ULID of the package", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
):
    if not validate_ulid(package_id):
        raise AppException(
            status_code=400,
            code="400",
            message="Invalid ULID format"
        )
    
    package_service = PackageService(db)
    db_package = package_service.get_package(package_id)
    if db_package is None:
        raise AppException(
            status_code=404,
            code="404",
            message="Package not found"
        )
    return {
        "status": True,
        "code": "10003",
        "message": "Package fetched successfully",
        "data": db_package
    }


@log_errors(api_logger)
@router.put("/{package_id}", response_model=BaseResponse[PackageSchema])
def update_package(
    package: PackageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("update_package")),
    package_id: str = Path(..., description="ULID of the package", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
):
    if not validate_ulid(package_id):
        raise AppException(
            status_code=400,
            code="400",
            message="Invalid ULID format"
        )
    
    package_service = PackageService(db)
    db_package = package_service.update_package(package_id, package, updated_by=current_user.id)
    if db_package is None:
        raise AppException(
            status_code=404,
            code="404",
            message="Package not found"
        )
    return {
        "status": True,
        "code": "10004",
        "message": "Package updated successfully",
        "data": db_package
    }


@log_errors(api_logger)
@router.delete("/{package_id}", response_model=BaseResponse[dict])
def delete_package(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("delete_package")),
    package_id: str = Path(..., description="ULID of the package", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
):
    if not validate_ulid(package_id):
        raise AppException(
            status_code=400,
            code="400",
            message="Invalid ULID format"
        )
    
    package_service = PackageService(db)
    if not package_service.delete_package(package_id, deleted_by=current_user.id):
        raise AppException(
            status_code=404,
            code="404",
            message="Package not found"
        )
    return {
        "status": True,
        "code": "10005",
        "message": "Package deleted successfully",
        "data": None
    }


@log_errors(api_logger)
@router.post("/{package_id}/restore", response_model=BaseResponse[dict])
def restore_package(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("delete_package")),
    package_id: str = Path(..., description="ULID of the package", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
):
    if not validate_ulid(package_id):
        raise AppException(
            status_code=400,
            code="400",
            message="Invalid ULID format"
        )
    
    package_service = PackageService(db)
    if not package_service.restore_package(package_id):
        raise AppException(
            status_code=404,
            code="404",
            message="Package not found or not deleted"
        )
    return {
        "status": True,
        "code": "10006",
        "message": "Package restored successfully",
        "data": None
    }


# Package Coverage endpoints
@log_errors(api_logger)
@router.post("/{package_id}/coverages/", response_model=BaseResponse[PackageCoverageSchema], status_code=status.HTTP_201_CREATED)
def create_package_coverage(
    package_coverage: PackageCoverageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("create_package"))
):
    package_coverage_service = PackageCoverageService(db)
    created_package_coverage = package_coverage_service.create_package_coverage(package_coverage, created_by=current_user.id)
    return {
        "status": True,
        "code": "10007",
        "message": "Package coverage created successfully",
        "data": created_package_coverage
    }


@log_errors(api_logger)
@router.get("/{package_id}/coverages/", response_model=BaseResponse[List[PackageCoverageSchema]])
def read_package_coverages(
    package_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("read_package"))
):
    if not validate_ulid(package_id):
        raise AppException(
            status_code=400,
            code="400",
            message="Invalid ULID format"
        )
    
    package_coverage_service = PackageCoverageService(db)
    package_coverages = package_coverage_service.get_coverages_by_package(package_id)
    return {
        "status": True,
        "code": "10008",
        "message": "Package coverages fetched successfully",
        "data": package_coverages
    }


@log_errors(api_logger)
@router.put("coverages/{package_coverage_id}", response_model=BaseResponse[PackageCoverageSchema])
def update_package_coverage(
    package_coverage: PackageCoverageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("update_package")),
    package_coverage_id: str = Path(..., description="ULID of the package coverage", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
):
    if not validate_ulid(package_coverage_id):
        raise AppException(
            status_code=400,
            code="400",
            message="Invalid ULID format"
        )
    
    package_coverage_service = PackageCoverageService(db)
    db_package_coverage = package_coverage_service.update_package_coverage(package_coverage_id, package_coverage, updated_by=current_user.id)
    if db_package_coverage is None:
        raise AppException(
            status_code=404,
            code="404",
            message="Package coverage not found"
        )
    return {
        "status": True,
        "code": "10009",
        "message": "Package coverage updated successfully",
        "data": db_package_coverage
    }


@log_errors(api_logger)
@router.delete("coverages/{package_coverage_id}", response_model=BaseResponse[dict])
def delete_package_coverage(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("delete_package")),
    package_coverage_id: str = Path(..., description="ULID of the package coverage", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
):
    if not validate_ulid(package_coverage_id):
        raise AppException(
            status_code=400,
            code="400",
            message="Invalid ULID format"
        )
    
    package_coverage_service = PackageCoverageService(db)
    if not package_coverage_service.delete_package_coverage(package_coverage_id, deleted_by=current_user.id):
        raise AppException(
            status_code=404,
            code="404",
            message="Package coverage not found"
        )
    return {
        "status": True,
        "code": "10010",
        "message": "Package coverage deleted successfully",
        "data": None
    }
