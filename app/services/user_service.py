from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash
from app.utils.ulid import validate_ulid
from app.utils.audit import set_audit_fields, soft_delete_record
from app.utils.logging_system import log_errors, system_logger


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_user(self, user_id: str) -> Optional[dict]:
        if not validate_ulid(user_id):
            return None
        user = self.db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        if not user:
            return None
            
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "roles": [
                {
                    "id": role.id,
                    "name": role.name,
                    "description": role.description
                }
                for role in user.roles
            ]
        }

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email, User.is_deleted == False).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username, User.is_deleted == False).first()

    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        users = self.db.query(User).filter(User.is_deleted == False).offset(skip).limit(limit).all()
        
        # Add roles to each user
        result = []
        for user in users:
            user_dict = {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "created_at": user.created_at,
                "updated_at": user.updated_at,
                "roles": [
                    {
                        "id": role.id,
                        "name": role.name,
                        "description": role.description
                    }
                    for role in user.roles
                ]
            }
            result.append(user_dict)
        
        return result

    def create_user(self, user: UserCreate, created_by: str = None) -> User:
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            hashed_password=hashed_password,
            is_active=user.is_active
        )
        set_audit_fields(db_user, created_by=created_by)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        # Assign default role if provided
        if hasattr(user, 'role_id') and user.role_id:
            from app.models.role import Role
            role = self.db.query(Role).filter(Role.id == user.role_id).first()
            if role:
                db_user.roles.append(role)
                self.db.commit()
                self.db.refresh(db_user)
        
        return db_user

    def update_user(
        self,
        user_id: str,
        user: UserUpdate,
        updated_by: str = None
    ) -> Optional[User]:
        if not validate_ulid(user_id):
            return None

        db_user = self.db.query(User).filter(
            User.id == user_id,
            User.is_deleted == False
        ).first()

        if not db_user:
            return None

        update_data = user.dict(exclude_unset=True)

        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(
                update_data.pop("password")
            )

        # jangan update role_id langsung ke table users
        role_id = update_data.pop("role_id", None)

        for field, value in update_data.items():
            setattr(db_user, field, value)

        if role_id:
            from app.models.role import Role

            role = self.db.query(Role).filter(Role.id == role_id).first()
            if role:
                db_user.roles.clear()
                db_user.roles.append(role)

        set_audit_fields(db_user, updated_by=updated_by)

        self.db.commit()
        self.db.refresh(db_user)

        return db_user

    def delete_user(
        self,
        user_id: str,
        deleted_by: str = None
    ) -> bool:

        if not validate_ulid(user_id):
            return False

        db_user = self.db.query(User).filter(
            User.id == user_id,
            User.is_deleted == False
        ).first()

        if not db_user:
            return False

        soft_delete_record(
            db_user,
            deleted_by=deleted_by
        )

        self.db.commit()

        return True

    def hard_delete_user(self, user_id: str) -> bool:
        """Permanently delete a user (use with caution)"""
        if not validate_ulid(user_id):
            return False
        db_user = self.db.query(User).filter(User.id == user_id).first()
        if db_user:
            self.db.delete(db_user)
            self.db.commit()
            return True
        return False

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = self.get_user_by_username(username)
        if not user:
            return None
        from app.core.security import verify_password
        if not verify_password(password, user.hashed_password):
            return None
        return user
