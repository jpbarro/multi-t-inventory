from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, declared_attr
from sqlalchemy import DateTime, ForeignKey, func
import uuid
from sqlalchemy.dialects.postgresql import UUID


class TimestampMixin:
    """
    Mixin that adds created_at and updated_at columns to a model.
    """

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class TenantAwareMixin:
    """
    Mixin that adds tenant_id to a model and creates the relationship.
    """

    @declared_attr
    def tenant_id(cls) -> Mapped[uuid.UUID]:
        return mapped_column(
            UUID(as_uuid=True),
            ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
