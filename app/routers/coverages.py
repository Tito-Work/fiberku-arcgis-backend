from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.coverage import Coverage as CoverageSchema, CoverageCreate, CoverageUpdate
from app.services.coverage_service import CoverageService
from app.middleware.rbac import get_current_user_with_permission
from app.models.user import User
from app.utils.ulid import validate_ulid
from app.schemas.base_response import BaseResponse
from app.exceptions.http_exception import AppException
from app.utils.logging_system import log_errors, api_logger

router = APIRouter()


@log_errors(api_logger)
@router.post("", response_model=BaseResponse[CoverageSchema], status_code=status.HTTP_201_CREATED)
def create_coverage(
    coverage: CoverageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("create_coverage"))
):
    coverage_service = CoverageService(db)
    
    if coverage_service.get_coverage_by_area(coverage.area):
        raise AppException(
            status_code=400,
            code="400",
            message="Coverage area already exists"
        )
    
    created_coverage = coverage_service.create_coverage(coverage, created_by=current_user.id)
    return {
        "status": True,
        "code": "10001",
        "message": "Coverage created successfully",
        "data": created_coverage
    }


@log_errors(api_logger)
@router.get("", response_model=BaseResponse[List[CoverageSchema]])
def read_coverages(
    skip: int = 0,
    limit: int = 100,
    has_capacity: bool = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("read_coverage"))
):
    coverage_service = CoverageService(db)
    
    if has_capacity is not None:
        coverages = coverage_service.get_coverages_with_capacity(has_capacity)
    else:
        coverages = coverage_service.get_coverages(skip=skip, limit=limit)
    
    return {
        "status": True,
        "code": "10002",
        "message": "Coverages fetched successfully",
        "data": coverages
    }


@log_errors(api_logger)
@router.get("/{coverage_id}", response_model=BaseResponse[CoverageSchema])
def read_coverage(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("read_coverage")),
    coverage_id: str = Path(..., description="ULID of the coverage", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
):
    if not validate_ulid(coverage_id):
        raise AppException(
            status_code=400,
            code="400",
            message="Invalid ULID format"
        )
    
    coverage_service = CoverageService(db)
    db_coverage = coverage_service.get_coverage(coverage_id)
    if db_coverage is None:
        raise AppException(
            status_code=404,
            code="404",
            message="Coverage not found"
        )
    return {
        "status": True,
        "code": "10003",
        "message": "Coverage fetched successfully",
        "data": db_coverage
    }


@log_errors(api_logger)
@router.put("/{coverage_id}", response_model=BaseResponse[CoverageSchema])
def update_coverage(
    coverage: CoverageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("update_coverage")),
    coverage_id: str = Path(..., description="ULID of the coverage", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
):
    if not validate_ulid(coverage_id):
        raise AppException(
            status_code=400,
            code="400",
            message="Invalid ULID format"
        )
    
    coverage_service = CoverageService(db)
    db_coverage = coverage_service.update_coverage(coverage_id, coverage, updated_by=current_user.id)
    if db_coverage is None:
        raise AppException(
            status_code=404,
            code="404",
            message="Coverage not found"
        )
    return {
        "status": True,
        "code": "10004",
        "message": "Coverage updated successfully",
        "data": db_coverage
    }


@log_errors(api_logger)
@router.delete("/{coverage_id}", response_model=BaseResponse[dict])
def delete_coverage(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("delete_coverage")),
    coverage_id: str = Path(..., description="ULID of the coverage", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
):
    if not validate_ulid(coverage_id):
        raise AppException(
            status_code=400,
            code="400",
            message="Invalid ULID format"
        )
    
    coverage_service = CoverageService(db)
    if not coverage_service.delete_coverage(coverage_id, deleted_by=current_user.id):
        raise AppException(
            status_code=404,
            code="404",
            message="Coverage not found"
        )
    return {
        "status": True,
        "code": "10005",
        "message": "Coverage deleted successfully",
        "data": None
    }


@log_errors(api_logger)
@router.post("/{coverage_id}/restore", response_model=BaseResponse[dict])
def restore_coverage(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("delete_coverage")),
    coverage_id: str = Path(..., description="ULID of the coverage", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
):
    if not validate_ulid(coverage_id):
        raise AppException(
            status_code=400,
            code="400",
            message="Invalid ULID format"
        )
    
    coverage_service = CoverageService(db)
    if not coverage_service.restore_coverage(coverage_id):
        raise AppException(
            status_code=404,
            code="404",
            message="Coverage not found or not deleted"
        )
    return {
        "status": True,
        "code": "10006",
        "message": "Coverage restored successfully",
        "data": None
    }


@log_errors(api_logger)
@router.post("/{coverage_id}/increment-customers", response_model=BaseResponse[dict])
def increment_customer_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("update_coverage")),
    coverage_id: str = Path(..., description="ULID of the coverage", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
):
    if not validate_ulid(coverage_id):
        raise AppException(
            status_code=400,
            code="400",
            message="Invalid ULID format"
        )
    
    coverage_service = CoverageService(db)
    if not coverage_service.increment_customer_count(coverage_id):
        raise AppException(
            status_code=404,
            code="404",
            message="Coverage not found or at maximum capacity"
        )
    return {
        "status": True,
        "code": "10007",
        "message": "Customer count incremented successfully",
        "data": None
    }


@log_errors(api_logger)
@router.post("/{coverage_id}/decrement-customers", response_model=BaseResponse[dict])
def decrement_customer_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("update_coverage")),
    coverage_id: str = Path(..., description="ULID of the coverage", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
):
    if not validate_ulid(coverage_id):
        raise AppException(
            status_code=400,
            code="400",
            message="Invalid ULID format"
        )
    
    coverage_service = CoverageService(db)
    if not coverage_service.decrement_customer_count(coverage_id):
        raise AppException(
            status_code=404,
            code="404",
            message="Coverage not found or no customers to decrement"
        )
    return {
        "status": True,
        "code": "10008",
        "message": "Customer count decremented successfully",
        "data": None
    }
