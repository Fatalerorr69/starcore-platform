"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-07-13

"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "blueprint_runs",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("blueprint_name", sa.String(), nullable=False),
        sa.Column("version", sa.String(), nullable=False),
        sa.Column("parallel", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "task_runs",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("run_id", sa.String(), sa.ForeignKey("blueprint_runs.id"), nullable=False),
        sa.Column("task_id", sa.String(), nullable=False),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("resource", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("result", sa.JSON(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("task_runs")
    op.drop_table("blueprint_runs")
