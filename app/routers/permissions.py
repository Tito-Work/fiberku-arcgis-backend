from typing import List
from fastapi import APIRouter, Depends, status, Path
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.permission import Permission as PermissionSchema, PermissionCreate
from app.services.permission_service import PermissionService
from app.middleware.rbac import get_current_user_with_permission
from app.models.user import User
from app.schemas.base_response import BaseResponse
from app.exceptions.http_exception import AppException
from app.utils.logging_system import log_errors, api_logger

router = APIRouter()


@log_errors(api_logger)
@router.get("", response_model=BaseResponse[List[PermissionSchema]])
def read_permissions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("read_role"))
):
    permission_service = PermissionService(db)
    permissions = permission_service.get_permissions(skip=skip, limit=limit)
    return {
        "status": True,
        "code": "10009",
        "message": "Permissions fetched successfully",
        "data": permissions
    }


@log_errors(api_logger)
@router.get("/{permission_id}", response_model=BaseResponse[PermissionSchema])
def read_permission(
    permission_id: str = Path(..., description="ULID of the permission", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$'),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("read_role"))
):
    permission_service = PermissionService(db)
    permission = permission_service.get_permission(permission_id)
    if permission is None:
        raise AppException(
            status_code=404,
            code="404",
            message="Permission not found"
        )
    return {
        "status": True,
        "code": "10010",
        "message": "Permission fetched successfully",
        "data": permission
    }


@log_errors(api_logger)
@router.post("", response_model=BaseResponse[PermissionSchema], status_code=status.HTTP_201_CREATED)
def create_permission(
    permission: PermissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("create_role"))
):
    permission_service = PermissionService(db)
    created_permission = permission_service.create_permission(permission.dict(), created_by=current_user.id)
    return {
        "status": True,
        "code": "10008",
        "message": "Permission created successfully",
        "data": created_permission
    }


@log_errors(api_logger)
@router.get("/by-resource/{resource}", response_model=BaseResponse[List[PermissionSchema]])
def read_permissions_by_resource(
    resource: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("read_role"))
):
    permission_service = PermissionService(db)
    permissions = permission_service.get_permissions_by_resource(resource)
    return {
        "status": True,
        "code": "10010",
        "message": "Permissions by resource fetched successfully",
        "data": permissions
    }


@log_errors(api_logger)
@router.put("/{permission_id}", response_model=BaseResponse[PermissionSchema])
def update_permission(
    permission: PermissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("update_role")),
    permission_id: str = Path(..., description="ULID of the permission", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
):
    permission_service = PermissionService(db)
    updated_permission = permission_service.update_permission(permission_id, permission.dict(), updated_by=current_user.id)
    if updated_permission is None:
        raise AppException(
            status_code=404,
            code="404",
            message="Permission not found"
        )
    return {
        "status": True,
        "code": "10014",
        "message": "Permission updated successfully",
        "data": updated_permission
    }


@log_errors(api_logger)
@router.delete("/{permission_id}", response_model=BaseResponse[dict])
def delete_permission(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("update_role")),
    permission_id: str = Path(..., description="ULID of the permission", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
):
    permission_service = PermissionService(db)
    if not permission_service.delete_permission(permission_id, deleted_by=current_user.id):
        raise AppException(
            status_code=404,
            code="404",
            message="Permission not found"
        )
    return {
        "status": True,
        "code": "10015",
        "message": "Permission deleted successfully",
        "data": None
    }
