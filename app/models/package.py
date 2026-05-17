from sqlalchemy import Column, String, Boolean, Text, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.utils.ulid import ULIDType, generate_ulid


class Package(BaseModel):
    __tablename__ = "packages"

    id = Column(ULIDType, primary_key=True, default=generate_ulid, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(DECIMAL(10, 2), nullable=False)
    color = Column(String(15), nullable=True)
    is_active = Column(Boolean, default=True)

    # Relationships
    customers = relationship("Customer", back_populates="package")
    package_coverages = relationship("PackageCoverage", back_populates="package")

    def __repr__(self):
        return f"<Package(id={self.id}, name={self.name}, price={self.price})>"


class PackageCoverage(BaseModel):
    __tablename__ = "package_coverages"

    id = Column(ULIDType, primary_key=True, default=generate_ulid, index=True)
    package_id = Column(ULIDType, ForeignKey("packages.id"), nullable=False)
    coverage_id = Column(ULIDType, ForeignKey("coverages.id"), nullable=False)
    is_active = Column(Boolean, default=True)

    # Relationships
    package = relationship("Package", back_populates="package_coverages")
    coverage = relationship("Coverage", back_populates="package_coverages")

    def __repr__(self):
        return f"<PackageCoverage(package_id={self.package_id}, coverage_id={self.coverage_id})>"
