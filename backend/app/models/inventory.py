from app.db.session import Base
from app.models.mixins import TenantAwareMixin
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import relationship

class Inventory(Base, TenantAwareMixin):
    __tablename__ = "inventories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    
    min_stock = Column(Integer, default=0)
    current_stock = Column(Integer, default=0)

    product = relationship("Product", back_populates="inventories")
    tenant = relationship("Tenant", back_populates="inventories")

    __table_args__ = (
        UniqueConstraint('tenant_id', 'product_id', name='uq_tenant_product_stock'),
    )