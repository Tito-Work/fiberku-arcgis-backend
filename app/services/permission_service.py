from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.role import Permission
from app.utils.ulid import validate_ulid
from app.utils.audit import set_audit_fields, soft_delete_record


class PermissionService:
    def __init__(self, db: Session):
        self.db = db

    def get_permission(self, permission_id: str) -> Optional[Permission]:
        if not validate_ulid(permission_id):
            return None
        return self.db.query(Permission).filter(Permission.id == permission_id, Permission.is_deleted == False).first()

    def get_permission_by_name(self, name: str) -> Optional[Permission]:
        return self.db.query(Permission).filter(Permission.name == name, Permission.is_deleted == False).first()

    def get_permissions(self, skip: int = 0, limit: int = 100) -> List[Permission]:
        return self.db.query(Permission).filter(Permission.is_deleted == False).offset(skip).limit(limit).all()

    def get_permissions_by_resource(self, resource: str) -> List[Permission]:
        return self.db.query(Permission).filter(Permission.resource == resource, Permission.is_deleted == False).all()

    def create_permission(self, permission_data: dict, created_by: str = None) -> Permission:
        permission = Permission(**permission_data)
        set_audit_fields(permission, created_by=created_by)
        self.db.add(permission)
        self.db.commit()
        self.db.refresh(permission)
        return permission

    def update_permission(self, permission_id: str, permission_data: dict, updated_by: str = None) -> Optional[Permission]:
        if not validate_ulid(permission_id):
            return None

        permission = self.get_permission(permission_id)
        if permission is None:
            return None

        for field, value in permission_data.items():
            setattr(permission, field, value)

        set_audit_fields(permission, updated_by=updated_by)
        self.db.commit()
        self.db.refresh(permission)
        return permission

    def delete_permission(self, permission_id: str, deleted_by: str = None) -> bool:
        if not validate_ulid(permission_id):
            return False

        permission = self.get_permission(permission_id)
        if permission is None:
            return False

        if soft_delete_record(permission, deleted_by):
            self.db.commit()
            return True
        return False
