"""add description to products

Revision ID: 0002_add_product_description
Revises: 0001_create_products
Create Date: 2026-05-27
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_add_product_description"
down_revision = "0001_create_products"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "products",
        sa.Column(
            "description",
            sa.String(length=500),
            nullable=False,
            server_default="No description",
        ),
    )


def downgrade() -> None:
    op.drop_column("products", "description")
