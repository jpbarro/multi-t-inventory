"""drop inventory quantity column

Revision ID: a1b2c3d4e5f6
Revises: 0e0ccc22938b
Create Date: 2026-02-13 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "0e0ccc22938b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("inventories", "quantity")


def downgrade() -> None:
    op.add_column("inventories", sa.Column("quantity", sa.Integer(), server_default="0", nullable=True))
