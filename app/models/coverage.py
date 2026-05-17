from sqlalchemy import Column, String, Boolean, Integer
from geoalchemy2 import Geometry
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.utils.ulid import ULIDType, generate_ulid


class Coverage(BaseModel):
    __tablename__ = "coverages"

    id = Column(ULIDType, primary_key=True, default=generate_ulid, index=True)
    area = Column(String(255), nullable=False)
    current_customer = Column(Integer, default=0)
    max_customer = Column(Integer, nullable=False)
    location = Column(Geometry('POLYGON', srid=4326), nullable=True)  # Native PostGIS POLYGON
    is_active = Column(Boolean, default=True)

    # Relationships
    package_coverages = relationship("PackageCoverage", back_populates="coverage")

    def __repr__(self):
        return f"<Coverage(id={self.id}, area={self.area}, capacity={self.current_customer}/{self.max_customer})>"
