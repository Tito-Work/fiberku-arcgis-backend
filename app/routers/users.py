from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user import User as UserSchema, UserCreate, UserUpdate
from app.services.user_service import UserService
from app.middleware.auth import get_current_active_user, get_current_user
from app.middleware.rbac import get_current_user_with_permission
from app.models.user import User
from app.utils.ulid import validate_ulid
from app.schemas.base_response import BaseResponse
from app.exceptions.http_exception import AppException
from app.utils.logging_system import log_errors, api_logger

router = APIRouter()


@log_errors(api_logger)
@router.post("", response_model=BaseResponse[UserSchema], status_code=status.HTTP_201_CREATED)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("create_user"))
):
    user_service = UserService(db)
    
    # Check if user already exists
    if user_service.get_user_by_email(user.email):
        raise AppException(
            status_code=400,
            code="400",
            message="Email already registered"
        )
    
    if user_service.get_user_by_username(user.username):
        raise AppException(
            status_code=400,
            code="400",
            message="Username already taken"
        )

    created_user = user_service.create_user(
        user,
        created_by=current_user.id
    )
    
    return {
        "status": True,
        "code": "10001",
        "message": "User created successfully",
        "data": created_user
    }


@log_errors(api_logger)
@router.get("", response_model=BaseResponse[List[UserSchema]])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("read_user"))
):
    user_service = UserService(db)
    users = user_service.get_users(skip=skip, limit=limit)

    return {
        "status": True,
        "code": "10002",
        "message": "Users fetched successfully",
        "data": users
    }


@log_errors(api_logger)
@router.get("me", response_model=BaseResponse[dict])
def read_user_me(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user with roles and permissions"""
    # Extract roles
    roles = [
        {
            "id": role.id,
            "name": role.name,
            "description": role.description
        }
        for role in current_user.roles
    ]
    
    # Extract permissions (unique from all roles)
    permissions = []
    seen_permissions = set()
    
    for role in current_user.roles:
        for permission in role.permissions:
            if permission.name not in seen_permissions:
                permissions.append({
                    "id": permission.id,
                    "name": permission.name,
                    "description": permission.description,
                    "resource": permission.resource
                })
                seen_permissions.add(permission.name)
    
    # Build user data with roles and permissions
    user_data = {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at,
        "roles": roles,
        "permissions": permissions
    }
    
    return {
        "status": True,
        "code": "10003",
        "message": "Current user fetched successfully",
        "data": user_data
    }


@log_errors(api_logger)
@router.get("me/roles", response_model=BaseResponse[List])
def read_user_me_roles(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's roles"""
    from app.schemas.role import Role as RoleSchema
    
    roles = [
        {
            "id": role.id,
            "name": role.name,
            "description": role.description
        }
        for role in current_user.roles
    ]
    
    return {
        "status": True,
        "code": "10004",
        "message": "User roles fetched successfully",
        "data": roles
    }


@log_errors(api_logger)
@router.get("me/permissions", response_model=BaseResponse[List])
def read_user_me_permissions(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's permissions (derived from roles)"""
    permissions = []
    seen_permissions = set()
    
    for role in current_user.roles:
        for permission in role.permissions:
            if permission.name not in seen_permissions:
                permissions.append({
                    "id": permission.id,
                    "name": permission.name,
                    "description": permission.description,
                    "resource": permission.resource
                })
                seen_permissions.add(permission.name)
    
    return {
        "status": True,
        "code": "10005",
        "message": "User permissions fetched successfully",
        "data": permissions
    }


@log_errors(api_logger)
@router.get("/{user_id}", response_model=BaseResponse[UserSchema])
def read_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("read_user")),
    user_id: str = Path(..., description="ULID of the user", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
):
    if not validate_ulid(user_id):
        raise AppException(
            status_code=400,
            code="400",
            message="Invalid ULID format"
        )
    
    user_service = UserService(db)
    db_user = user_service.get_user(user_id)
    if db_user is None:
        raise AppException(
            status_code=404,
            code="404",
            message="User not found"
        )
    return {
        "status": True,
        "code": "10004",
        "message": "User fetched successfully",
        "data": db_user
    }


@log_errors(api_logger)
@router.put("/{user_id}", response_model=BaseResponse[UserSchema])
def update_user(
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("update_user")),
    user_id: str = Path(..., description="ULID of the user", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
):
    if not validate_ulid(user_id):
        raise AppException(
            status_code=400,
            code="400",
            message="Invalid ULID format"
        )
    
    user_service = UserService(db)
    db_user = user_service.update_user(user_id, user, updated_by=current_user.id)
    if db_user is None:
        raise AppException(
            status_code=404,
            code="404",
            message="User not found"
        )
    return {
        "status": True,
        "code": "10005",
        "message": "User updated successfully",
        "data": db_user
    }


@log_errors(api_logger)
@router.delete("/{user_id}")
def delete_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("delete_user")),
    user_id: str = Path(..., description="ULID of the user", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
):
    if not validate_ulid(user_id):
        raise AppException(
            status_code=400,
            code="400",
            message="Invalid ULID format"
        )
    
    user_service = UserService(db)
    if not user_service.delete_user(user_id, deleted_by=current_user.id):
        raise AppException(
            status_code=404,
            code="404",
            message="User not found"
        )
    return {
        "status": True,
        "code": "10006",
        "message": "User deleted successfully",
        "data": None
    }
