from typing import List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.customer import Customer
from app.models.coverage import Coverage
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.utils.ulid import validate_ulid
from app.utils.audit import set_audit_fields, soft_delete_record
from app.utils.geo import serialize_geometry


class CustomerService:
    def __init__(self, db: Session):
        self.db = db

    def _find_coverage_for_point(self, point) -> Optional[Coverage]:
        if not point:
            return None
        return (
            self.db.query(Coverage)
            .filter(Coverage.is_deleted == False)
            .filter(func.ST_Contains(Coverage.location, point))
            .first()
        )

    def _increment_current_customer_for_point(self, point) -> bool:
        coverage = self._find_coverage_for_point(point)
        if not coverage:
            return False
        if coverage.current_customer >= coverage.max_customer:
            return False
        coverage.current_customer += 1
        self.db.commit()
        return True

    def _decrement_current_customer_for_point(self, point) -> bool:
        coverage = self._find_coverage_for_point(point)
        if not coverage:
            return False
        if coverage.current_customer <= 0:
            return False
        coverage.current_customer -= 1
        self.db.commit()
        return True

    def get_customer(self, customer_id: str) -> Optional[Customer]:
        if not validate_ulid(customer_id):
            return None
        return self.db.query(Customer).filter(Customer.id == customer_id, Customer.is_deleted == False).first()

    def get_customer_by_code(self, code: str) -> Optional[Customer]:
        return self.db.query(Customer).filter(Customer.code == code, Customer.is_deleted == False).first()

    def get_customer_by_email(self, email: str) -> Optional[Customer]:
        return self.db.query(Customer).filter(Customer.email == email, Customer.is_deleted == False).first()

    def get_customers(self, skip: int = 0, limit: int = 100) -> List[Customer]:
        return self.db.query(Customer).filter(Customer.is_deleted == False).offset(skip).limit(limit).all()

    def create_customer(self, customer: CustomerCreate, created_by: str = None) -> Customer:
        db_customer = Customer(
            code=customer.code,
            name=customer.name,
            email=customer.email,
            phone=customer.phone,
            province=customer.province,
            city=customer.city,
            district=customer.district,
            subdistrict=customer.subdistrict,
            postcode=customer.postcode,
            address=customer.address,
            location=customer.location,
            package_id=customer.package_id,
            price=customer.price,
            is_active=customer.is_active
        )
        set_audit_fields(db_customer, created_by=created_by)
        self.db.add(db_customer)
        self.db.commit()
        self.db.refresh(db_customer)

        if db_customer.location:
            self._increment_current_customer_for_point(db_customer.location)
            db_customer.location = serialize_geometry(
                db_customer.location
            )
        return db_customer

    def update_customer(self, customer_id: str, customer: CustomerUpdate, updated_by: str = None) -> Optional[Customer]:
        if not validate_ulid(customer_id):
            return None
            
        db_customer = self.get_customer(customer_id)
        if db_customer:
            update_data = customer.dict(exclude_unset=True)
            old_location = db_customer.location if "location" in update_data else None

            for field, value in update_data.items():
                setattr(db_customer, field, value)
            
            set_audit_fields(db_customer, updated_by=updated_by)
            self.db.commit()
            self.db.refresh(db_customer)

            if "location" in update_data:
                if old_location:
                    self._decrement_current_customer_for_point(old_location)
                if db_customer.location:
                    self._increment_current_customer_for_point(db_customer.location)
            
            if db_customer.location:
                db_customer.location = serialize_geometry(
                    db_customer.location
                )
        return db_customer

    def delete_customer(self, customer_id: str, deleted_by: str = None) -> bool:
        if not validate_ulid(customer_id):
            return False
            
        db_customer = self.get_customer(customer_id)
        if db_customer:
            if db_customer.location:
                self._decrement_current_customer_for_point(db_customer.location)
            soft_delete_record(db_customer, deleted_by=deleted_by)
            self.db.commit()
            return True
        return False

    def restore_customer(self, customer_id: str) -> bool:
        if not validate_ulid(customer_id):
            return False
            
        db_customer = self.db.query(Customer).filter(Customer.id == customer_id, Customer.is_deleted == True).first()
        if db_customer:
            db_customer.restore()
            self.db.commit()
            return True
        return False

    def get_customers_by_package(self, package_id: str) -> List[Customer]:
        if not validate_ulid(package_id):
            return []
        return self.db.query(Customer).filter(
            Customer.package_id == package_id, 
            Customer.is_deleted == False
        ).all()

    def get_customers_by_city(self, city: str) -> List[Customer]:
        return self.db.query(Customer).filter(
            Customer.city == city,
            Customer.is_deleted == False
        ).all()
