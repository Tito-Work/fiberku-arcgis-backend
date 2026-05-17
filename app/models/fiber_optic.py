from sqlalchemy import Column, String, Boolean, ForeignKey
from geoalchemy2 import Geometry
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.utils.ulid import ULIDType, generate_ulid


class FiberOptic(BaseModel):
    __tablename__ = "fiber_optics"

    id = Column(ULIDType, primary_key=True, default=generate_ulid, index=True)
    segment_id = Column(ULIDType, ForeignKey("segments.id"), nullable=False)
    operator_id = Column(ULIDType, ForeignKey("operators.id"), nullable=False)
    location = Column(Geometry('LINESTRING', srid=4326), nullable=True)  # Native PostGIS LINESTRING
    is_active = Column(Boolean, default=True)

    # Relationships
    segment = relationship("Segment", back_populates="fiber_optics")
    operator = relationship("Operator", back_populates="fiber_optics")

    def __repr__(self):
        return f"<FiberOptic(id={self.id}, segment_id={self.segment_id}, operator_id={self.operator_id})>"
