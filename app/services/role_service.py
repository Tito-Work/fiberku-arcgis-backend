from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from app.models.role import Role, Permission
from app.models.user import User
from app.schemas.role import RoleCreate, RoleUpdate
from app.utils.ulid import validate_ulid
from app.utils.audit import set_audit_fields, soft_delete_record


class RoleService:
    def __init__(self, db: Session):
        self.db = db

    def get_role(self, role_id: str) -> Optional[Role]:
        if not validate_ulid(role_id):
            return None
        return self.db.query(Role).filter(Role.id == role_id, Role.is_deleted == False).first()

    def get_role_by_name(self, name: str) -> Optional[Role]:
        return self.db.query(Role).filter(Role.name == name, Role.is_deleted == False).first()

    def get_roles(self, skip: int = 0, limit: int = 100) -> List[Role]:
        return self.db.query(Role).options(
            joinedload(Role.permissions)
        ).filter(Role.is_deleted == False).offset(skip).limit(limit).all()

    def create_role(self, role: RoleCreate, created_by: str = None) -> Role:
        db_role = Role(
            name=role.name,
            description=role.description,
            is_active=role.is_active
        )
        
        set_audit_fields(db_role, created_by=created_by)
        
        # Add permissions if provided
        if role.permission_ids:
            permissions = self.db.query(Permission).filter(
                Permission.id.in_(role.permission_ids),
                Permission.is_deleted == False
            ).all()
            db_role.permissions = permissions
        
        self.db.add(db_role)
        self.db.commit()
        self.db.refresh(db_role)
        return db_role

    def update_role(self, role_id: str, role: RoleUpdate, updated_by: str = None) -> Optional[Role]:
        if not validate_ulid(role_id):
            return None
        db_role = self.get_role(role_id)
        if db_role is None:
            return None
        
        update_data = role.dict(exclude_unset=True)
        
        # Handle permission updates if provided
        permission_ids = update_data.pop("permission_ids", None)
        
        for field, value in update_data.items():
            setattr(db_role, field, value)
        
        set_audit_fields(db_role, updated_by=updated_by)
        
        # Update permissions if provided
        if permission_ids is not None:
            permissions = self.db.query(Permission).filter(
                Permission.id.in_(permission_ids),
                Permission.is_deleted == False
            ).all()
            db_role.permissions = permissions
        
        self.db.commit()
        self.db.refresh(db_role)
        return db_role

    def delete_role(self, role_id: str, deleted_by: str = None) -> bool:
        if not validate_ulid(role_id):
            return False
        db_role = self.get_role(role_id)
        if db_role:
            if soft_delete_record(db_role, deleted_by):
                self.db.commit()
                return True
        return False

    def assign_permission_to_role(self, role_id: str, permission_id: str) -> bool:
        if not validate_ulid(role_id) or not validate_ulid(permission_id):
            return False
        
        db_role = self.get_role(role_id)
        if db_role is None:
            return False
        
        permission = self.db.query(Permission).filter(
            Permission.id == permission_id,
            Permission.is_deleted == False
        ).first()
        
        if permission is None:
            return False
        
        # Check if permission is already assigned
        if permission in db_role.permissions:
            return True  # Already assigned
        
        db_role.permissions.append(permission)
        self.db.commit()
        self.db.refresh(db_role)
        return True

    def remove_permission_from_role(self, role_id: str, permission_id: str) -> bool:
        if not validate_ulid(role_id) or not validate_ulid(permission_id):
            return False
        
        db_role = self.get_role(role_id)
        if db_role is None:
            return False
        
        permission = self.db.query(Permission).filter(
            Permission.id == permission_id,
            Permission.is_deleted == False
        ).first()
        
        if permission is None:
            return False
        
        # Check if permission is assigned
        if permission not in db_role.permissions:
            return True  # Already removed
        
        db_role.permissions.remove(permission)
        self.db.commit()
        self.db.refresh(db_role)
        return True

    def hard_delete_role(self, role_id: str) -> bool:
        """Permanently delete a role (use with caution)"""
        if not validate_ulid(role_id):
            return False
        db_role = self.db.query(Role).filter(Role.id == role_id).first()
        if db_role:
            self.db.delete(db_role)
            self.db.commit()
            return True
        return False

    def assign_role_to_user(self, user_id: str, role_id: str) -> bool:
        if not validate_ulid(user_id) or not validate_ulid(role_id):
            return False
        user = self.db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        role = self.get_role(role_id)
        
        if user and role:
            if role not in user.roles:
                user.roles.append(role)
                self.db.commit()
            return True
        return False

    def remove_role_from_user(self, user_id: str, role_id: str) -> bool:
        if not validate_ulid(user_id) or not validate_ulid(role_id):
            return False
        user = self.db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        role = self.get_role(role_id)
        
        if user and role and role in user.roles:
            user.roles.remove(role)
            self.db.commit()
            return True
        return False

    def get_user_roles(self, user_id: str) -> List[Role]:
        if not validate_ulid(user_id):
            return []
        user = self.db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        return user.roles if user else []



