from sqlalchemy import Column, String, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import BaseModel
from app.utils.ulid import ULIDType, generate_ulid

# Association table for many-to-many relationship between users and roles
user_roles = Table(
    'user_roles',
    BaseModel.metadata,
    Column('user_id', ULIDType, ForeignKey('users.id'), primary_key=True),
    Column('role_id', ULIDType, ForeignKey('roles.id'), primary_key=True),
    Column('created_at', DateTime(timezone=True), server_default=func.now())
)

# Association table for many-to-many relationship between roles and permissions
role_permissions = Table(
    'role_permissions',
    BaseModel.metadata,
    Column('role_id', ULIDType, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', ULIDType, ForeignKey('permissions.id'), primary_key=True),
    Column('created_at', DateTime(timezone=True), server_default=func.now())
)

class Role(BaseModel):
    __tablename__ = "roles"
    id = Column(ULIDType, primary_key=True, default=generate_ulid, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    is_active = Column(String, default=True)
    
    # Relationships
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")
    users = relationship("User", secondary=user_roles, back_populates="roles")

class Permission(BaseModel):
    __tablename__ = "permissions"
    id = Column(ULIDType, primary_key=True, default=generate_ulid, index=True)
    name = Column(String(100), unique=True, nullable=False)
    resource = Column(String(50), nullable=False)
    action = Column(String(50), nullable=False)
    description = Column(String(255))
    
    # Relationships
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")