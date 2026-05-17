from sqlalchemy import Column, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import declared_attr, relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.utils.ulid import ULIDType


class AuditMixin:
    """Mixin class to add audit fields to models"""
    
    @declared_attr
    def created_by(cls):
        return Column(ULIDType, ForeignKey('users.id'), nullable=True)
    
    @declared_attr
    def updated_by(cls):
        return Column(ULIDType, ForeignKey('users.id'), nullable=True)
    
    @declared_attr
    def deleted_by(cls):
        return Column(ULIDType, ForeignKey('users.id'), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    is_deleted = Column(Boolean, default=False)
    
    @declared_attr
    def creator(cls):
        return relationship("User", foreign_keys=[cls.created_by], lazy='select')
    
    @declared_attr
    def updater(cls):
        return relationship("User", foreign_keys=[cls.updated_by], lazy='select')
    
    @declared_attr
    def deleter(cls):
        return relationship("User", foreign_keys=[cls.deleted_by], lazy='select')


class BaseModel(Base, AuditMixin):
    """Base model class with audit fields and soft delete functionality"""
    
    __abstract__ = True
    
    def soft_delete(self, deleted_by_user_id=None):
        """Mark the record as deleted"""
        self.is_deleted = True
        self.deleted_at = func.now()
        if deleted_by_user_id:
            self.deleted_by = deleted_by_user_id
    
    def restore(self):
        """Restore a soft-deleted record"""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
