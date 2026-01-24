"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2026-01-23

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create products table
    op.create_table('products',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('gtin', sa.String(length=50), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('brand', sa.String(length=255), nullable=True),
        sa.Column('image_url', sa.Text(), nullable=True),
        sa.Column('source', sa.Enum('MANUAL', 'OPENFOODFACTS', 'UPCITEMDB', 'BARCODELOOKUP', 'UNKNOWN', name='productsource'), nullable=False),
        sa.Column('raw_payload', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_products_gtin'), 'products', ['gtin'], unique=True)
    
    # Create inventory_items table
    op.create_table('inventory_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('location', sa.String(length=255), nullable=False),
        sa.Column('quantity', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('unit', sa.String(length=50), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_inventory_items_product_id'), 'inventory_items', ['product_id'], unique=False)
    
    # Create inventory_transactions table
    op.create_table('inventory_transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('inventory_item_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('delta', sa.Integer(), nullable=False),
        sa.Column('reason', sa.Enum('ADD', 'REMOVE', 'ADJUST', name='transactionreason'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['inventory_item_id'], ['inventory_items.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_inventory_transactions_inventory_item_id'), 'inventory_transactions', ['inventory_item_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_inventory_transactions_inventory_item_id'), table_name='inventory_transactions')
    op.drop_table('inventory_transactions')
    op.drop_index(op.f('ix_inventory_items_product_id'), table_name='inventory_items')
    op.drop_table('inventory_items')
    op.drop_index(op.f('ix_products_gtin'), table_name='products')
    op.drop_table('products')
