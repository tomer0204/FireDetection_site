"""recreate tracks and detections tables

Revision ID: 2c91a8f4b123
Revises: 1b41734d4a9c
Create Date: 2026-01-27
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "2c91a8f4b123"
down_revision = "1b41734d4a9c"
branch_labels = None
depends_on = None


def upgrade():
    # --- tracks ---
    op.create_table(
        "tracks",
        sa.Column("track_id", sa.Integer(), primary_key=True),
        sa.Column("camera_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now()
        ),
        sa.ForeignKeyConstraint(
            ["camera_id"],
            ["cameras.camera_id"],
            ondelete="CASCADE"
        ),
    )

    # --- detections ---
    op.create_table(
        "detections",
        sa.Column("detection_id", sa.Integer(), primary_key=True),
        sa.Column("camera_id", sa.Integer(), nullable=False),
        sa.Column("track_id", sa.Integer(), nullable=False),
        sa.Column("coordinates", postgresql.JSON(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now()
        ),
        sa.ForeignKeyConstraint(
            ["camera_id"],
            ["cameras.camera_id"],
            ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["track_id"],
            ["tracks.track_id"],
            ondelete="CASCADE"
        ),
    )


def downgrade():
    op.drop_table("detections")
    op.drop_table("tracks")
