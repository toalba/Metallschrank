"""add_opengtindb_provider_to_source_enum

Revision ID: a1046c1cf86c
Revises: 001
Create Date: 2026-01-23 23:59:13.188410

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1046c1cf86c'
down_revision: Union[str, Sequence[str], None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add 'opengtindb' to the productsource enum if it doesn't exist
    op.execute("ALTER TYPE productsource ADD VALUE IF NOT EXISTS 'opengtindb'")


def downgrade() -> None:
    """Downgrade schema."""
    # Cannot remove enum values in PostgreSQL easily
    # Would require recreating the enum type
    pass
