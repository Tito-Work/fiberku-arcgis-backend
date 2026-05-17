from sqlalchemy import Column, String, Boolean, ForeignKey, Text, Integer, DECIMAL
from geoalchemy2 import Geometry
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.utils.ulid import ULIDType, generate_ulid


class Customer(BaseModel):
    __tablename__ = "customers"

    id = Column(ULIDType, primary_key=True, default=generate_ulid, index=True)
    code = Column(String(50), unique=True, nullable=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    phone = Column(String(50), nullable=True)
    province = Column(String(50), nullable=True)
    city = Column(String(100), nullable=True)
    district = Column(String(50), nullable=True)
    subdistrict = Column(String(50), nullable=True)
    postcode = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    location = Column(Geometry('POINT', srid=4326), nullable=True)  # Native PostGIS POINT
    package_id = Column(ULIDType, ForeignKey("packages.id"), nullable=True)
    price = Column(DECIMAL(10, 2), nullable=True)
    is_active = Column(Boolean, default=True)

    # Relationships
    package = relationship("Package", back_populates="customers")

    def __repr__(self):
        return f"<Customer(id={self.id}, name={self.name}, code={self.code})>"
