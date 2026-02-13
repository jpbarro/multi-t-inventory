from app.db.session import Base
from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import relationship


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    sku = Column(String, unique=True, index=True)

    inventories = relationship("Inventory", back_populates="product")
