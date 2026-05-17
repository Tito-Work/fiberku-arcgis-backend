from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.coverage import Coverage
from app.schemas.coverage import CoverageCreate, CoverageUpdate
from app.utils.ulid import validate_ulid
from app.utils.audit import set_audit_fields, soft_delete_record
from geoalchemy2.shape import to_shape
from geoalchemy2.elements import WKBElement


class CoverageService:
    def __init__(self, db: Session):
        self.db = db

    def _convert_location_to_wkt(self, coverage: Coverage) -> Coverage:
        """Convert WKBElement location to WKT string for serialization"""
        if coverage.location and isinstance(coverage.location, WKBElement):
            geom = to_shape(coverage.location)
            coverage.location = geom.wkt
        return coverage

    def get_coverage(self, coverage_id: str) -> Optional[Coverage]:
        if not validate_ulid(coverage_id):
            return None
        return self.db.query(Coverage).filter(Coverage.id == coverage_id, Coverage.is_deleted == False).first()

    def get_coverage_by_area(self, area: str) -> Optional[Coverage]:
        return self.db.query(Coverage).filter(Coverage.area == area, Coverage.is_deleted == False).first()

    def get_coverages(self, skip: int = 0, limit: int = 100) -> List[Coverage]:
        return self.db.query(Coverage).filter(Coverage.is_deleted == False).offset(skip).limit(limit).all()

    def create_coverage(self, coverage: CoverageCreate, created_by: str = None) -> Coverage:
        db_coverage = Coverage(
            area=coverage.area,
            current_customer=coverage.current_customer,
            max_customer=coverage.max_customer,
            location=coverage.location,
            is_active=coverage.is_active
        )
        set_audit_fields(db_coverage, created_by=created_by)
        self.db.add(db_coverage)
        self.db.commit()
        self.db.refresh(db_coverage)
        return self._convert_location_to_wkt(db_coverage)

    def update_coverage(self, coverage_id: str, coverage: CoverageUpdate, updated_by: str = None) -> Optional[Coverage]:
        if not validate_ulid(coverage_id):
            return None
            
        db_coverage = self.get_coverage(coverage_id)
        if db_coverage:
            update_data = coverage.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_coverage, field, value)
            
            set_audit_fields(db_coverage, updated_by=updated_by)
            self.db.commit()
            self.db.refresh(db_coverage)
        return db_coverage

    def delete_coverage(self, coverage_id: str, deleted_by: str = None) -> bool:
        if not validate_ulid(coverage_id):
            return False
            
        db_coverage = self.get_coverage(coverage_id)
        if db_coverage:
            soft_delete_record(db_coverage, deleted_by=deleted_by)
            self.db.commit()
            return True
        return False

    def restore_coverage(self, coverage_id: str) -> bool:
        if not validate_ulid(coverage_id):
            return False
            
        db_coverage = self.db.query(Coverage).filter(Coverage.id == coverage_id, Coverage.is_deleted == True).first()
        if db_coverage:
            db_coverage.restore()
            self.db.commit()
            return True
        return False

    def get_coverages_with_capacity(self, has_capacity: bool = True) -> List[Coverage]:
        if has_capacity:
            return self.db.query(Coverage).filter(
                Coverage.current_customer < Coverage.max_customer,
                Coverage.is_deleted == False
            ).all()
        else:
            return self.db.query(Coverage).filter(
                Coverage.current_customer >= Coverage.max_customer,
                Coverage.is_deleted == False
            ).all()

    def increment_customer_count(self, coverage_id: str) -> bool:
        if not validate_ulid(coverage_id):
            return False
            
        db_coverage = self.get_coverage(coverage_id)
        if db_coverage and db_coverage.current_customer < db_coverage.max_customer:
            db_coverage.current_customer += 1
            self.db.commit()
            return True
        return False

    def decrement_customer_count(self, coverage_id: str) -> bool:
        if not validate_ulid(coverage_id):
            return False
            
        db_coverage = self.get_coverage(coverage_id)
        if db_coverage and db_coverage.current_customer > 0:
            db_coverage.current_customer -= 1
            self.db.commit()
            return True
        return False
