from sqlalchemy import Boolean, Column, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True)

    tenant = relationship("Tenant", back_populates="users")
