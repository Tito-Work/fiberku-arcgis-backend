from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.segment import Segment
from app.schemas.segment import SegmentCreate, SegmentUpdate
from app.utils.ulid import validate_ulid
from app.utils.audit import set_audit_fields, soft_delete_record


class SegmentService:
    def __init__(self, db: Session):
        self.db = db

    def get_segment(self, segment_id: str) -> Optional[Segment]:
        if not validate_ulid(segment_id):
            return None
        return self.db.query(Segment).filter(Segment.id == segment_id, Segment.is_deleted == False).first()

    def get_segment_by_code(self, code: str) -> Optional[Segment]:
        return self.db.query(Segment).filter(Segment.code == code, Segment.is_deleted == False).first()

    def get_segments(self, skip: int = 0, limit: int = 100) -> List[Segment]:
        return self.db.query(Segment).filter(Segment.is_deleted == False).offset(skip).limit(limit).all()

    def create_segment(self, segment: SegmentCreate, created_by: str = None) -> Segment:
        db_segment = Segment(
            code=segment.code,
            name=segment.name,
            is_active=segment.is_active
        )
        set_audit_fields(db_segment, created_by=created_by)
        self.db.add(db_segment)
        self.db.commit()
        self.db.refresh(db_segment)
        return db_segment

    def update_segment(self, segment_id: str, segment: SegmentUpdate, updated_by: str = None) -> Optional[Segment]:
        if not validate_ulid(segment_id):
            return None
            
        db_segment = self.get_segment(segment_id)
        if db_segment:
            update_data = segment.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_segment, field, value)
            
            set_audit_fields(db_segment, updated_by=updated_by)
            self.db.commit()
            self.db.refresh(db_segment)
        return db_segment

    def delete_segment(self, segment_id: str, deleted_by: str = None) -> bool:
        if not validate_ulid(segment_id):
            return False
            
        db_segment = self.get_segment(segment_id)
        if db_segment:
            soft_delete_record(db_segment, deleted_by=deleted_by)
            self.db.commit()
            return True
        return False

    def restore_segment(self, segment_id: str) -> bool:
        if not validate_ulid(segment_id):
            return False
            
        db_segment = self.db.query(Segment).filter(Segment.id == segment_id, Segment.is_deleted == True).first()
        if db_segment:
            db_segment.restore()
            self.db.commit()
            return True
        return False

    def get_active_segments(self) -> List[Segment]:
        return self.db.query(Segment).filter(Segment.is_active == True, Segment.is_deleted == False).all()
