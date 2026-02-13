from sqlalchemy.orm import Mapped, mapped_column, declared_attr
from sqlalchemy import ForeignKey
import uuid
from sqlalchemy.dialects.postgresql import UUID


class TenantAwareMixin:
    """
    Mixin that adds tenant_id to a model and creates the relationship.
    """

    @declared_attr
    def tenant_id(cls) -> Mapped[uuid.UUID]:
        return mapped_column(
            UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True
        )
