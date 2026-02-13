from app.db.session import Base
from app.models.mixins import TimestampMixin
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import relationship


class Tenant(Base, TimestampMixin):
    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    inventories = relationship("Inventory", back_populates="tenant")
    users = relationship("User", back_populates="tenant")
