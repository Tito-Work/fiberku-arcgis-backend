from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.utils.ulid import ULIDType, generate_ulid


class Operator(BaseModel):
    __tablename__ = "operators"

    id = Column(ULIDType, primary_key=True, default=generate_ulid, index=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)

    # Relationships
    fiber_optics = relationship("FiberOptic", back_populates="operator")

    def __repr__(self):
        return f"<Operator(id={self.id}, code={self.code}, name={self.name})>"
