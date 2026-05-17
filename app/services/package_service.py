from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.package import Package, PackageCoverage
from app.schemas.package import PackageCreate, PackageUpdate, PackageCoverageCreate, PackageCoverageUpdate
from app.utils.ulid import validate_ulid
from app.utils.audit import set_audit_fields, soft_delete_record


class PackageService:
    def __init__(self, db: Session):
        self.db = db

    def get_package(self, package_id: str) -> Optional[Package]:
        if not validate_ulid(package_id):
            return None
        return self.db.query(Package).filter(Package.id == package_id, Package.is_deleted == False).first()

    def get_package_by_name(self, name: str) -> Optional[Package]:
        return self.db.query(Package).filter(Package.name == name, Package.is_deleted == False).first()

    def get_packages(self, skip: int = 0, limit: int = 100) -> List[Package]:
        return self.db.query(Package).filter(Package.is_deleted == False).offset(skip).limit(limit).all()

    def create_package(self, package: PackageCreate, created_by: str = None) -> Package:
        db_package = Package(
            name=package.name,
            description=package.description,
            price=package.price,
            is_active=package.is_active
        )
        set_audit_fields(db_package, created_by=created_by)
        self.db.add(db_package)
        self.db.commit()
        self.db.refresh(db_package)
        return db_package

    def update_package(self, package_id: str, package: PackageUpdate, updated_by: str = None) -> Optional[Package]:
        if not validate_ulid(package_id):
            return None
            
        db_package = self.get_package(package_id)
        if db_package:
            update_data = package.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_package, field, value)
            
            set_audit_fields(db_package, updated_by=updated_by)
            self.db.commit()
            self.db.refresh(db_package)
        return db_package

    def delete_package(self, package_id: str, deleted_by: str = None) -> bool:
        if not validate_ulid(package_id):
            return False
            
        db_package = self.get_package(package_id)
        if db_package:
            soft_delete_record(db_package, deleted_by=deleted_by)
            self.db.commit()
            return True
        return False

    def restore_package(self, package_id: str) -> bool:
        if not validate_ulid(package_id):
            return False
            
        db_package = self.db.query(Package).filter(Package.id == package_id, Package.is_deleted == True).first()
        if db_package:
            db_package.restore()
            self.db.commit()
            return True
        return False


class PackageCoverageService:
    def __init__(self, db: Session):
        self.db = db

    def get_package_coverage(self, package_coverage_id: str) -> Optional[PackageCoverage]:
        if not validate_ulid(package_coverage_id):
            return None
        return self.db.query(PackageCoverage).filter(
            PackageCoverage.id == package_coverage_id, 
            PackageCoverage.is_deleted == False
        ).first()

    def get_package_coverages(self, skip: int = 0, limit: int = 100) -> List[PackageCoverage]:
        return self.db.query(PackageCoverage).filter(PackageCoverage.is_deleted == False).offset(skip).limit(limit).all()

    def get_coverages_by_package(self, package_id: str) -> List[PackageCoverage]:
        if not validate_ulid(package_id):
            return []
        return self.db.query(PackageCoverage).filter(
            PackageCoverage.package_id == package_id,
            PackageCoverage.is_deleted == False
        ).all()

    def get_packages_by_coverage(self, coverage_id: str) -> List[PackageCoverage]:
        if not validate_ulid(coverage_id):
            return []
        return self.db.query(PackageCoverage).filter(
            PackageCoverage.coverage_id == coverage_id,
            PackageCoverage.is_deleted == False
        ).all()

    def create_package_coverage(self, package_coverage: PackageCoverageCreate, created_by: str = None) -> PackageCoverage:
        db_package_coverage = PackageCoverage(
            package_id=package_coverage.package_id,
            coverage_id=package_coverage.coverage_id,
            is_active=package_coverage.is_active
        )
        set_audit_fields(db_package_coverage, created_by=created_by)
        self.db.add(db_package_coverage)
        self.db.commit()
        self.db.refresh(db_package_coverage)
        return db_package_coverage

    def update_package_coverage(self, package_coverage_id: str, package_coverage: PackageCoverageUpdate, updated_by: str = None) -> Optional[PackageCoverage]:
        if not validate_ulid(package_coverage_id):
            return None
            
        db_package_coverage = self.get_package_coverage(package_coverage_id)
        if db_package_coverage:
            update_data = package_coverage.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_package_coverage, field, value)
            
            set_audit_fields(db_package_coverage, updated_by=updated_by)
            self.db.commit()
            self.db.refresh(db_package_coverage)
        return db_package_coverage

    def delete_package_coverage(self, package_coverage_id: str, deleted_by: str = None) -> bool:
        if not validate_ulid(package_coverage_id):
            return False
            
        db_package_coverage = self.get_package_coverage(package_coverage_id)
        if db_package_coverage:
            soft_delete_record(db_package_coverage, deleted_by=deleted_by)
            self.db.commit()
            return True
        return False

    def restore_package_coverage(self, package_coverage_id: str) -> bool:
        if not validate_ulid(package_coverage_id):
            return False
            
        db_package_coverage = self.db.query(PackageCoverage).filter(
            PackageCoverage.id == package_coverage_id, 
            PackageCoverage.is_deleted == True
        ).first()
        if db_package_coverage:
            db_package_coverage.restore()
            self.db.commit()
            return True
        return False
