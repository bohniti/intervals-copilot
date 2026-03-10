"""add intervals_activity_id — already included in initial migration (no-op)

Revision ID: a1b2c3d4e5f6
Revises: cc006a6af522
Create Date: 2026-03-09 14:00:00
"""
from alembic import op

revision = "a1b2c3d4e5f6"
down_revision = "cc006a6af522"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # intervals_activity_id is already included in the initial migration.
    pass


def downgrade() -> None:
    pass
