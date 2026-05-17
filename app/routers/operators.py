from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.operator import Operator as OperatorSchema, OperatorCreate, OperatorUpdate
from app.services.operator_service import OperatorService
from app.middleware.rbac import get_current_user_with_permission
from app.models.user import User
from app.utils.ulid import validate_ulid
from app.schemas.base_response import BaseResponse
from app.exceptions.http_exception import AppException
from app.utils.logging_system import log_errors, api_logger

router = APIRouter()


@log_errors(api_logger)
@router.post("", response_model=BaseResponse[OperatorSchema], status_code=status.HTTP_201_CREATED)
def create_operator(
    operator: OperatorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("create_operator"))
):
    operator_service = OperatorService(db)
    
    if operator_service.get_operator_by_code(operator.code):
        raise AppException(
            status_code=400,
            code="400",
            message="Operator code already exists"
        )
    
    created_operator = operator_service.create_operator(operator, created_by=current_user.id)
    return {
        "status": True,
        "code": "10001",
        "message": "Operator created successfully",
        "data": created_operator
    }


@log_errors(api_logger)
@router.get("", response_model=BaseResponse[List[OperatorSchema]])
def read_operators(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("read_operator"))
):
    operator_service = OperatorService(db)
    
    if active_only:
        operators = operator_service.get_active_operators()
    else:
        operators = operator_service.get_operators(skip=skip, limit=limit)
    
    return {
        "status": True,
        "code": "10002",
        "message": "Operators fetched successfully",
        "data": operators
    }


@log_errors(api_logger)
@router.get("/{operator_id}", response_model=BaseResponse[OperatorSchema])
def read_operator(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("read_operator")),
    operator_id: str = Path(..., description="ULID of the operator", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
):
    if not validate_ulid(operator_id):
        raise AppException(
            status_code=400,
            code="400",
            message="Invalid ULID format"
        )
    
    operator_service = OperatorService(db)
    db_operator = operator_service.get_operator(operator_id)
    if db_operator is None:
        raise AppException(
            status_code=404,
            code="404",
            message="Operator not found"
        )
    return {
        "status": True,
        "code": "10003",
        "message": "Operator fetched successfully",
        "data": db_operator
    }


@log_errors(api_logger)
@router.put("/{operator_id}", response_model=BaseResponse[OperatorSchema])
def update_operator(
    operator: OperatorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("update_operator")),
    operator_id: str = Path(..., description="ULID of the operator", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
):
    if not validate_ulid(operator_id):
        raise AppException(
            status_code=400,
            code="400",
            message="Invalid ULID format"
        )
    
    operator_service = OperatorService(db)
    db_operator = operator_service.update_operator(operator_id, operator, updated_by=current_user.id)
    if db_operator is None:
        raise AppException(
            status_code=404,
            code="404",
            message="Operator not found"
        )
    return {
        "status": True,
        "code": "10004",
        "message": "Operator updated successfully",
        "data": db_operator
    }


@log_errors(api_logger)
@router.delete("/{operator_id}", response_model=BaseResponse[dict])
def delete_operator(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("delete_operator")),
    operator_id: str = Path(..., description="ULID of the operator", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
):
    if not validate_ulid(operator_id):
        raise AppException(
            status_code=400,
            code="400",
            message="Invalid ULID format"
        )
    
    operator_service = OperatorService(db)
    if not operator_service.delete_operator(operator_id, deleted_by=current_user.id):
        raise AppException(
            status_code=404,
            code="404",
            message="Operator not found"
        )
    return {
        "status": True,
        "code": "10005",
        "message": "Operator deleted successfully",
        "data": None
    }


@log_errors(api_logger)
@router.post("/{operator_id}/restore", response_model=BaseResponse[dict])
def restore_operator(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("delete_operator")),
    operator_id: str = Path(..., description="ULID of the operator", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
):
    if not validate_ulid(operator_id):
        raise AppException(
            status_code=400,
            code="400",
            message="Invalid ULID format"
        )
    
    operator_service = OperatorService(db)
    if not operator_service.restore_operator(operator_id):
        raise AppException(
            status_code=404,
            code="404",
            message="Operator not found or not deleted"
        )
    return {
        "status": True,
        "code": "10006",
        "message": "Operator restored successfully",
        "data": None
    }
