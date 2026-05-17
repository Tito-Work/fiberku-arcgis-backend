from datetime import timedelta
from typing import Dict
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.database import get_db
from app.core.security import (
    create_access_token, 
    create_refresh_token, 
    decode_token,
    verify_token
)
from app.core.config import settings
from app.schemas.user import Token
from app.services.user_service import UserService
from app.middleware.auth import get_current_active_user
from app.schemas.base_response import BaseResponse
from app.exceptions.http_exception import AppException
from app.models.user import User
from app.utils.logging_system import log_errors, auth_logger

router = APIRouter()


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=BaseResponse[dict])
@log_errors(auth_logger)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    user = user_service.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    refresh_token_expires = timedelta(days=7)
    
    # Create tokens
    access_token = create_access_token(
        data={"sub": user.username}, 
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": user.username}, 
        expires_delta=refresh_token_expires
    )
    
    # Extract roles and permissions for the user
    roles = [
        {
            "id": role.id,
            "name": role.name,
            "description": role.description
        }
        for role in user.roles
    ]
    
    # Extract permissions (unique from all roles)
    permissions = []
    seen_permissions = set()
    
    for role in user.roles:
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
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "roles": roles,
        "permissions": permissions
    }
    
    return {
        "status": True,
        "code": "10000",
        "message": "Login successful",
        "data": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user_data
        }
    }


@router.post("/refresh", response_model=BaseResponse[dict])
@log_errors(auth_logger)
async def refresh_access_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    
    # Verify refresh token
    payload = decode_token(request.refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check token type
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user_service = UserService(db)
    user = user_service.get_user_by_username(username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create new tokens
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    refresh_token_expires = timedelta(days=7)
    
    new_access_token = create_access_token(
        data={"sub": user.username}, 
        expires_delta=access_token_expires
    )
    new_refresh_token = create_refresh_token(
        data={"sub": user.username}, 
        expires_delta=refresh_token_expires
    )
    
    return {
        "status": True,
        "code": "10002",
        "message": "Token refreshed successfully",
        "data": {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
    }


@router.post("/logout", response_model=BaseResponse[dict])
@log_errors(auth_logger)
async def logout(
    current_user: User = Depends(get_current_active_user)
):
    """
    Logout endpoint. 
    In a production system, you would typically blacklist the token here.
    For JWT-based auth, the client simply discards the tokens.
    """
    return {
        "status": True,
        "code": "10003",
        "message": "Logged out successfully",
        "data": None
    }


class PermissionCheckRequest(BaseModel):
    permission: str


@router.post("/check-permission", response_model=BaseResponse[Dict])
@log_errors(auth_logger)
def check_permission(
    request: PermissionCheckRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Check if current user has a specific permission.
    Useful for server-side validation from frontend.
    """
    has_permission = current_user.has_permission(request.permission)
    
    return {
        "status": True,
        "code": "10001",
        "message": "Permission check completed",
        "data": {
            "has_permission": has_permission,
            "permission": request.permission,
            "user_id": current_user.id
        }
    }