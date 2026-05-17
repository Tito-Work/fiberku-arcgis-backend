"""
Models package initialization
"""

from app.core.database import Base

from app.models.user import User
from app.models.role import Role, Permission

__all__ = ["Base", "User", "Role", "Permission"]