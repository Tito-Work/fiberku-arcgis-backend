from sqlalchemy.orm import Query
from app.models.base import BaseModel


class SoftDeleteQuery(Query):
    """Custom Query class that automatically filters out soft-deleted records"""
    
    def __new__(cls, *args, **kwargs):
        query = super().__new__(cls, *args, **kwargs)
        if hasattr(query.column_descriptions[0]['type'], '__tablename__'):
            # Only apply soft delete filter to models that inherit from BaseModel
            if issubclass(query.column_descriptions[0]['type'], BaseModel):
                query = query.filter(BaseModel.is_deleted == False)
        return query


def set_audit_fields(model_instance, created_by=None, updated_by=None):
    """Set audit fields on a model instance"""
    if created_by and hasattr(model_instance, 'created_by'):
        model_instance.created_by = created_by
    if updated_by and hasattr(model_instance, 'updated_by'):
        model_instance.updated_by = updated_by


def soft_delete_record(model_instance, deleted_by=None):
    """Soft delete a record"""
    if hasattr(model_instance, 'soft_delete'):
        model_instance.soft_delete(deleted_by)
        return True
    return False


def restore_record(model_instance):
    """Restore a soft-deleted record"""
    if hasattr(model_instance, 'restore'):
        model_instance.restore()
        return True
    return False
