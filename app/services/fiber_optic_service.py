from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.fiber_optic import FiberOptic
from app.schemas.fiber_optic import FiberOpticCreate, FiberOpticUpdate
from app.utils.ulid import validate_ulid
from app.utils.audit import set_audit_fields, soft_delete_record
from app.utils.geo import serialize_geometry


class FiberOpticService:
    def __init__(self, db: Session):
        self.db = db

    def get_fiber_optic(self, fiber_optic_id: str) -> Optional[FiberOptic]:
        if not validate_ulid(fiber_optic_id):
            return None
        return self.db.query(FiberOptic).filter(FiberOptic.id == fiber_optic_id, FiberOptic.is_deleted == False).first()

    def get_fiber_optics(self, skip: int = 0, limit: int = 100) -> List[FiberOptic]:
        return self.db.query(FiberOptic).filter(FiberOptic.is_deleted == False).offset(skip).limit(limit).all()

    def create_fiber_optic(self, fiber_optic: FiberOpticCreate, created_by: str = None) -> FiberOptic:
        db_fiber_optic = FiberOptic(
            segment_id=fiber_optic.segment_id,
            operator_id=fiber_optic.operator_id,
            location=fiber_optic.location,
            is_active=fiber_optic.is_active
        )

        set_audit_fields(db_fiber_optic, created_by=created_by)

        self.db.add(db_fiber_optic)
        self.db.commit()
        self.db.refresh(db_fiber_optic)

        db_fiber_optic.location = serialize_geometry(db_fiber_optic.location)

        return db_fiber_optic

    def update_fiber_optic(self, fiber_optic_id: str, fiber_optic: FiberOpticUpdate, updated_by: str = None) -> Optional[FiberOptic]:
        if not validate_ulid(fiber_optic_id):
            return None
            
        db_fiber_optic = self.get_fiber_optic(fiber_optic_id)
        if db_fiber_optic:
            update_data = fiber_optic.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_fiber_optic, field, value)
            
            set_audit_fields(db_fiber_optic, updated_by=updated_by)
            self.db.commit()
            self.db.refresh(db_fiber_optic)
        return db_fiber_optic

    def delete_fiber_optic(self, fiber_optic_id: str, deleted_by: str = None) -> bool:
        if not validate_ulid(fiber_optic_id):
            return False
            
        db_fiber_optic = self.get_fiber_optic(fiber_optic_id)
        if db_fiber_optic:
            soft_delete_record(db_fiber_optic, deleted_by=deleted_by)
            self.db.commit()
            return True
        return False

    def restore_fiber_optic(self, fiber_optic_id: str) -> bool:
        if not validate_ulid(fiber_optic_id):
            return False
            
        db_fiber_optic = self.db.query(FiberOptic).filter(FiberOptic.id == fiber_optic_id, FiberOptic.is_deleted == True).first()
        if db_fiber_optic:
            db_fiber_optic.restore()
            self.db.commit()
            return True
        return False

    def get_fiber_optics_by_segment(self, segment_id: str) -> List[FiberOptic]:
        if not validate_ulid(segment_id):
            return []
        return self.db.query(FiberOptic).filter(
            FiberOptic.segment_id == segment_id,
            FiberOptic.is_deleted == False
        ).all()

    def get_fiber_optics_by_operator(self, operator_id: str) -> List[FiberOptic]:
        if not validate_ulid(operator_id):
            return []
        return self.db.query(FiberOptic).filter(
            FiberOptic.operator_id == operator_id,
            FiberOptic.is_deleted == False
        ).all()

    def get_active_fiber_optics(self) -> List[FiberOptic]:
        return self.db.query(FiberOptic).filter(FiberOptic.is_active == True, FiberOptic.is_deleted == False).all()
