from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.segment import Segment as SegmentSchema, SegmentCreate, SegmentUpdate
from app.services.segment_service import SegmentService
from app.middleware.rbac import get_current_user_with_permission
from app.models.user import User
from app.utils.ulid import validate_ulid
from app.schemas.base_response import BaseResponse
from app.exceptions.http_exception import AppException
from app.utils.logging_system import log_errors, api_logger

router = APIRouter()


@log_errors(api_logger)
@router.post("", response_model=BaseResponse[SegmentSchema], status_code=status.HTTP_201_CREATED)
def create_segment(
    segment: SegmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("create_segment"))
):
    segment_service = SegmentService(db)
    
    if segment_service.get_segment_by_code(segment.code):
        raise AppException(
            status_code=400,
            code="400",
            message="Segment code already exists"
        )
    
    created_segment = segment_service.create_segment(segment, created_by=current_user.id)
    return {
        "status": True,
        "code": "10001",
        "message": "Segment created successfully",
        "data": created_segment
    }


@log_errors(api_logger)
@router.get("", response_model=BaseResponse[List[SegmentSchema]])
def read_segments(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("read_segment"))
):
    segment_service = SegmentService(db)
    
    if active_only:
        segments = segment_service.get_active_segments()
    else:
        segments = segment_service.get_segments(skip=skip, limit=limit)
    
    return {
        "status": True,
        "code": "10002",
        "message": "Segments fetched successfully",
        "data": segments
    }


@log_errors(api_logger)
@router.get("/{segment_id}", response_model=BaseResponse[SegmentSchema])
def read_segment(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("read_segment")),
    segment_id: str = Path(..., description="ULID of the segment", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
):
    if not validate_ulid(segment_id):
        raise AppException(
            status_code=400,
            code="400",
            message="Invalid ULID format"
        )
    
    segment_service = SegmentService(db)
    db_segment = segment_service.get_segment(segment_id)
    if db_segment is None:
        raise AppException(
            status_code=404,
            code="404",
            message="Segment not found"
        )
    return {
        "status": True,
        "code": "10003",
        "message": "Segment fetched successfully",
        "data": db_segment
    }


@log_errors(api_logger)
@router.put("/{segment_id}", response_model=BaseResponse[SegmentSchema])
def update_segment(
    segment: SegmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("update_segment")),
    segment_id: str = Path(..., description="ULID of the segment", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
):
    if not validate_ulid(segment_id):
        raise AppException(
            status_code=400,
            code="400",
            message="Invalid ULID format"
        )
    
    segment_service = SegmentService(db)
    db_segment = segment_service.update_segment(segment_id, segment, updated_by=current_user.id)
    if db_segment is None:
        raise AppException(
            status_code=404,
            code="404",
            message="Segment not found"
        )
    return {
        "status": True,
        "code": "10004",
        "message": "Segment updated successfully",
        "data": db_segment
    }


@log_errors(api_logger)
@router.delete("/{segment_id}", response_model=BaseResponse[dict])
def delete_segment(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("delete_segment")),
    segment_id: str = Path(..., description="ULID of the segment", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
):
    if not validate_ulid(segment_id):
        raise AppException(
            status_code=400,
            code="400",
            message="Invalid ULID format"
        )
    
    segment_service = SegmentService(db)
    if not segment_service.delete_segment(segment_id, deleted_by=current_user.id):
        raise AppException(
            status_code=404,
            code="404",
            message="Segment not found"
        )
    return {
        "status": True,
        "code": "10005",
        "message": "Segment deleted successfully",
        "data": None
    }


@log_errors(api_logger)
@router.post("/{segment_id}/restore", response_model=BaseResponse[dict])
def restore_segment(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("delete_segment")),
    segment_id: str = Path(..., description="ULID of the segment", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
):
    if not validate_ulid(segment_id):
        raise AppException(
            status_code=400,
            code="400",
            message="Invalid ULID format"
        )
    
    segment_service = SegmentService(db)
    if not segment_service.restore_segment(segment_id):
        raise AppException(
            status_code=404,
            code="404",
            message="Segment not found or not deleted"
        )
    return {
        "status": True,
        "code": "10006",
        "message": "Segment restored successfully",
        "data": None
    }
