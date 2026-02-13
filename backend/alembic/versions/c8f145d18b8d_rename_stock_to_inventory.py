"""rename stock to inventory

Revision ID: c8f145d18b8d
Revises: 38d205628af2
Create Date: 2026-02-12 18:15:49.982915

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c8f145d18b8d"
down_revision: Union[str, Sequence[str], None] = "38d205628af2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.rename_table("stocks", "inventories")

    op.drop_constraint("uq_tenant_product_stock", "inventories", type_="unique")
    op.create_unique_constraint(
        "uq_tenant_product_inventory", "inventories", ["tenant_id", "product_id"]
    )


def downgrade():
    op.drop_constraint("uq_tenant_product_inventory", "inventories", type_="unique")
    op.create_unique_constraint(
        "uq_tenant_product_stock", "inventories", ["tenant_id", "product_id"]
    )
    op.rename_table("inventories", "stocks")
