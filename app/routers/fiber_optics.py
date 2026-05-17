from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.fiber_optic import FiberOptic as FiberOpticSchema, FiberOpticCreate, FiberOpticUpdate
from app.services.fiber_optic_service import FiberOpticService
from app.middleware.rbac import get_current_user_with_permission
from app.models.user import User
from app.utils.ulid import validate_ulid
from app.schemas.base_response import BaseResponse
from app.exceptions.http_exception import AppException
from app.utils.logging_system import log_errors, api_logger

router = APIRouter()


@log_errors(api_logger)
@router.post("", response_model=BaseResponse[FiberOpticSchema], status_code=status.HTTP_201_CREATED)
def create_fiber_optic(
    fiber_optic: FiberOpticCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("create_fiber_optic"))
):
    fiber_optic_service = FiberOpticService(db)
    created_fiber_optic = fiber_optic_service.create_fiber_optic(fiber_optic, created_by=current_user.id)
    return {
        "status": True,
        "code": "10001",
        "message": "Fiber optic created successfully",
        "data": created_fiber_optic
    }


@log_errors(api_logger)
@router.get("", response_model=BaseResponse[List[FiberOpticSchema]])
def read_fiber_optics(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("read_fiber_optic"))
):
    fiber_optic_service = FiberOpticService(db)
    
    if active_only:
        fiber_optics = fiber_optic_service.get_active_fiber_optics()
    else:
        fiber_optics = fiber_optic_service.get_fiber_optics(skip=skip, limit=limit)
    
    return {
        "status": True,
        "code": "10002",
        "message": "Fiber optics fetched successfully",
        "data": fiber_optics
    }


@log_errors(api_logger)
@router.get("/{fiber_optic_id}", response_model=BaseResponse[FiberOpticSchema])
def read_fiber_optic(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("read_fiber_optic")),
    fiber_optic_id: str = Path(..., description="ULID of the fiber optic", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
):
    if not validate_ulid(fiber_optic_id):
        raise AppException(
            status_code=400,
            code="400",
            message="Invalid ULID format"
        )
    
    fiber_optic_service = FiberOpticService(db)
    db_fiber_optic = fiber_optic_service.get_fiber_optic(fiber_optic_id)
    if db_fiber_optic is None:
        raise AppException(
            status_code=404,
            code="404",
            message="Fiber optic not found"
        )
    return {
        "status": True,
        "code": "10003",
        "message": "Fiber optic fetched successfully",
        "data": db_fiber_optic
    }


@log_errors(api_logger)
@router.put("/{fiber_optic_id}", response_model=BaseResponse[FiberOpticSchema])
def update_fiber_optic(
    fiber_optic: FiberOpticUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("update_fiber_optic")),
    fiber_optic_id: str = Path(..., description="ULID of the fiber optic", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
):
    if not validate_ulid(fiber_optic_id):
        raise AppException(
            status_code=400,
            code="400",
            message="Invalid ULID format"
        )
    
    fiber_optic_service = FiberOpticService(db)
    db_fiber_optic = fiber_optic_service.update_fiber_optic(fiber_optic_id, fiber_optic, updated_by=current_user.id)
    if db_fiber_optic is None:
        raise AppException(
            status_code=404,
            code="404",
            message="Fiber optic not found"
        )
    return {
        "status": True,
        "code": "10004",
        "message": "Fiber optic updated successfully",
        "data": db_fiber_optic
    }


@log_errors(api_logger)
@router.delete("/{fiber_optic_id}", response_model=BaseResponse[dict])
def delete_fiber_optic(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("delete_fiber_optic")),
    fiber_optic_id: str = Path(..., description="ULID of the fiber optic", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
):
    if not validate_ulid(fiber_optic_id):
        raise AppException(
            status_code=400,
            code="400",
            message="Invalid ULID format"
        )
    
    fiber_optic_service = FiberOpticService(db)
    if not fiber_optic_service.delete_fiber_optic(fiber_optic_id, deleted_by=current_user.id):
        raise AppException(
            status_code=404,
            code="404",
            message="Fiber optic not found"
        )
    return {
        "status": True,
        "code": "10005",
        "message": "Fiber optic deleted successfully",
        "data": None
    }


@log_errors(api_logger)
@router.post("/{fiber_optic_id}/restore", response_model=BaseResponse[dict])
def restore_fiber_optic(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("delete_fiber_optic")),
    fiber_optic_id: str = Path(..., description="ULID of the fiber optic", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
):
    if not validate_ulid(fiber_optic_id):
        raise AppException(
            status_code=400,
            code="400",
            message="Invalid ULID format"
        )
    
    fiber_optic_service = FiberOpticService(db)
    if not fiber_optic_service.restore_fiber_optic(fiber_optic_id):
        raise AppException(
            status_code=404,
            code="404",
            message="Fiber optic not found or not deleted"
        )
    return {
        "status": True,
        "code": "10006",
        "message": "Fiber optic restored successfully",
        "data": None
    }


@log_errors(api_logger)
@router.get("by-segment/{segment_id}", response_model=BaseResponse[List[FiberOpticSchema]])
def get_fiber_optics_by_segment(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("read_fiber_optic")),
    segment_id: str = Path(..., description="ULID of the segment", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
):
    if not validate_ulid(segment_id):
        raise AppException(
            status_code=400,
            code="400",
            message="Invalid ULID format"
        )
    
    fiber_optic_service = FiberOpticService(db)
    fiber_optics = fiber_optic_service.get_fiber_optics_by_segment(segment_id)
    return {
        "status": True,
        "code": "10007",
        "message": "Fiber optics by segment fetched successfully",
        "data": fiber_optics
    }


@log_errors(api_logger)
@router.get("by-operator/{operator_id}", response_model=BaseResponse[List[FiberOpticSchema]])
def get_fiber_optics_by_operator(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("read_fiber_optic")),
    operator_id: str = Path(..., description="ULID of the operator", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
):
    if not validate_ulid(operator_id):
        raise AppException(
            status_code=400,
            code="400",
            message="Invalid ULID format"
        )
    
    fiber_optic_service = FiberOpticService(db)
    fiber_optics = fiber_optic_service.get_fiber_optics_by_operator(operator_id)
    return {
        "status": True,
        "code": "10008",
        "message": "Fiber optics by operator fetched successfully",
        "data": fiber_optics
    }
