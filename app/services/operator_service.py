from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.operator import Operator
from app.schemas.operator import OperatorCreate, OperatorUpdate
from app.utils.ulid import validate_ulid
from app.utils.audit import set_audit_fields, soft_delete_record


class OperatorService:
    def __init__(self, db: Session):
        self.db = db

    def get_operator(self, operator_id: str) -> Optional[Operator]:
        if not validate_ulid(operator_id):
            return None
        return self.db.query(Operator).filter(Operator.id == operator_id, Operator.is_deleted == False).first()

    def get_operator_by_code(self, code: str) -> Optional[Operator]:
        return self.db.query(Operator).filter(Operator.code == code, Operator.is_deleted == False).first()

    def get_operators(self, skip: int = 0, limit: int = 100) -> List[Operator]:
        return self.db.query(Operator).filter(Operator.is_deleted == False).offset(skip).limit(limit).all()

    def create_operator(self, operator: OperatorCreate, created_by: str = None) -> Operator:
        db_operator = Operator(
            code=operator.code,
            name=operator.name,
            is_active=operator.is_active
        )
        set_audit_fields(db_operator, created_by=created_by)
        self.db.add(db_operator)
        self.db.commit()
        self.db.refresh(db_operator)
        return db_operator

    def update_operator(self, operator_id: str, operator: OperatorUpdate, updated_by: str = None) -> Optional[Operator]:
        if not validate_ulid(operator_id):
            return None
            
        db_operator = self.get_operator(operator_id)
        if db_operator:
            update_data = operator.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_operator, field, value)
            
            set_audit_fields(db_operator, updated_by=updated_by)
            self.db.commit()
            self.db.refresh(db_operator)
        return db_operator

    def delete_operator(self, operator_id: str, deleted_by: str = None) -> bool:
        if not validate_ulid(operator_id):
            return False
            
        db_operator = self.get_operator(operator_id)
        if db_operator:
            soft_delete_record(db_operator, deleted_by=deleted_by)
            self.db.commit()
            return True
        return False

    def restore_operator(self, operator_id: str) -> bool:
        if not validate_ulid(operator_id):
            return False
            
        db_operator = self.db.query(Operator).filter(Operator.id == operator_id, Operator.is_deleted == True).first()
        if db_operator:
            db_operator.restore()
            self.db.commit()
            return True
        return False

    def get_active_operators(self) -> List[Operator]:
        return self.db.query(Operator).filter(Operator.is_active == True, Operator.is_deleted == False).all()
