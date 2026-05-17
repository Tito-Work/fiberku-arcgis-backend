from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.role import Role as RoleSchema, RoleCreate, RoleUpdate
from app.schemas.permission import Permission as PermissionSchema
from app.services.role_service import RoleService
from app.middleware.rbac import get_current_user_with_permission
from app.models.user import User
from app.utils.ulid import validate_ulid
from app.schemas.base_response import BaseResponse
from app.exceptions.http_exception import AppException
from app.utils.logging_system import log_errors, api_logger

router = APIRouter()


# Role endpoints
@log_errors(api_logger)
@router.post("", response_model=BaseResponse[RoleSchema], status_code=status.HTTP_201_CREATED)
def create_role(
    role: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("create_role"))
):
    role_service = RoleService(db)
    
    if role_service.get_role_by_name(role.name):
        raise AppException(
            status_code=400,
            code="400",
            message="Role already exists"
        )
    
    created_role = role_service.create_role(role, created_by=current_user.id)
    return {
        "status": True,
        "code": "10001",
        "message": "Role created successfully",
        "data": created_role
    }


@log_errors(api_logger)
@router.get("", response_model=BaseResponse[List[RoleSchema]])
def read_roles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("read_role"))
):
    role_service = RoleService(db)
    roles = role_service.get_roles(skip=skip, limit=limit)
    return {
        "status": True,
        "code": "10002",
        "message": "Roles fetched successfully",
        "data": roles
    }


@log_errors(api_logger)
@router.get("/{role_id}", response_model=BaseResponse[RoleSchema])
def read_role(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("read_role")),
    role_id: str = Path(..., description="ULID of the role", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
):
    if not validate_ulid(role_id):
        raise AppException(
            status_code=400,
            code="400",
            message="Invalid ULID format"
        )
    
    role_service = RoleService(db)
    db_role = role_service.get_role(role_id)
    if db_role is None:
        raise AppException(
            status_code=404,
            code="404",
            message="Role not found"
        )
    return {
        "status": True,
        "code": "10003",
        "message": "Role fetched successfully",
        "data": db_role
    }


@log_errors(api_logger)
@router.put("/{role_id}", response_model=BaseResponse[RoleSchema])
def update_role(
    role: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("update_role")),
    role_id: str = Path(..., description="ULID of the role", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
):
    if not validate_ulid(role_id):
        raise AppException(
            status_code=400,
            code="400",
            message="Invalid ULID format"
        )
    
    role_service = RoleService(db)
    db_role = role_service.update_role(role_id, role, updated_by=current_user.id)
    if db_role is None:
        raise AppException(
            status_code=404,
            code="404",
            message="Role not found"
        )
    return {
        "status": True,
        "code": "10004",
        "message": "Role updated successfully",
        "data": db_role
    }


@log_errors(api_logger)
@router.delete("/{role_id}", response_model=BaseResponse[dict])
def delete_role(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("delete_role")),
    role_id: str = Path(..., description="ULID of the role", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
):
    if not validate_ulid(role_id):
        raise AppException(
            status_code=400,
            code="400",
            message="Invalid ULID format"
        )
    
    role_service = RoleService(db)
    if not role_service.delete_role(role_id, deleted_by=current_user.id):
        raise AppException(
            status_code=404,
            code="404",
            message="Role not found"
        )
    return {
        "status": True,
        "code": "10005",
        "message": "Role deleted successfully",
        "data": None
    }


# User role assignment endpoints
@log_errors(api_logger)
@router.post("/{role_id}/users/{user_id}", response_model=BaseResponse[dict])
def assign_role_to_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("update_user")),
    role_id: str = Path(..., description="ULID of the role", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$'),
    user_id: str = Path(..., description="ULID of the user", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
):
    if not validate_ulid(role_id) or not validate_ulid(user_id):
        raise AppException(
            status_code=400,
            code="400",
            message="Invalid ULID format"
        )
    
    role_service = RoleService(db)
    if not role_service.assign_role_to_user(user_id, role_id):
        raise AppException(
            status_code=404,
            code="404",
            message="Role or user not found"
        )
    return {
        "status": True,
        "code": "10006",
        "message": "Role assigned to user successfully",
        "data": None
    }


@log_errors(api_logger)
@router.delete("/{role_id}/users/{user_id}", response_model=BaseResponse[dict])
def remove_role_from_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("update_user")),
    role_id: str = Path(..., description="ULID of the role", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$'),
    user_id: str = Path(..., description="ULID of the user", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
):
    if not validate_ulid(role_id) or not validate_ulid(user_id):
        raise AppException(
            status_code=400,
            code="400",
            message="Invalid ULID format"
        )
    
    role_service = RoleService(db)
    if not role_service.remove_role_from_user(user_id, role_id):
        raise AppException(
            status_code=404,
            code="404",
            message="Role or user not found"
        )
    return {
        "status": True,
        "code": "10007",
        "message": "Role removed from user successfully",
        "data": None
    }


# Role permission assignment endpoints
@log_errors(api_logger)
@router.post("/{role_id}/permissions/{permission_id}", response_model=BaseResponse[dict])
def assign_permission_to_role(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("update_role")),
    role_id: str = Path(..., description="ULID of the role", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$'),
    permission_id: str = Path(..., description="ULID of the permission", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
):
    if not validate_ulid(role_id) or not validate_ulid(permission_id):
        raise AppException(
            status_code=400,
            code="400",
            message="Invalid ULID format"
        )
    
    role_service = RoleService(db)
    if not role_service.assign_permission_to_role(role_id, permission_id):
        raise AppException(
            status_code=404,
            code="404",
            message="Role or permission not found"
        )
    return {
        "status": True,
        "code": "10011",
        "message": "Permission assigned to role successfully",
        "data": None
    }


@log_errors(api_logger)
@router.delete("/{role_id}/permissions/{permission_id}", response_model=BaseResponse[dict])
def remove_permission_from_role(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("update_role")),
    role_id: str = Path(..., description="ULID of the role", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$'),
    permission_id: str = Path(..., description="ULID of the permission", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
):
    if not validate_ulid(role_id) or not validate_ulid(permission_id):
        raise AppException(
            status_code=400,
            code="400",
            message="Invalid ULID format"
        )
    
    role_service = RoleService(db)
    if not role_service.remove_permission_from_role(role_id, permission_id):
        raise AppException(
            status_code=404,
            code="404",
            message="Role or permission not found"
        )
    return {
        "status": True,
        "code": "10012",
        "message": "Permission removed from role successfully",
        "data": None
    }


@log_errors(api_logger)
@router.get("/{role_id}/permissions", response_model=BaseResponse[List[PermissionSchema]])
def get_role_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("read_role")),
    role_id: str = Path(..., description="ULID of the role", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
):
    if not validate_ulid(role_id):
        raise AppException(
            status_code=400,
            code="400",
            message="Invalid ULID format"
        )
    
    role_service = RoleService(db)
    role = role_service.get_role(role_id)
    if role is None:
        raise AppException(
            status_code=404,
            code="404",
            message="Role not found"
        )
    return {
        "status": True,
        "code": "10013",
        "message": "Role permissions fetched successfully",
        "data": role.permissions
    }
