"""add account lockout, token version and refresh token family

Revision ID: 7c1f4a2b9d3e
Revises: 2a8b7c9d0e1f
"""

import sqlalchemy as sa
from alembic import op

revision = "7c1f4a2b9d3e"
down_revision = "2a8b7c9d0e1f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "usuarios",
        sa.Column("intentos_fallidos", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column("usuarios", sa.Column("bloqueado_hasta", sa.DateTime(), nullable=True))
    op.add_column(
        "usuarios",
        sa.Column("token_version", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "refresh_tokens",
        sa.Column("familia_id", sa.String(length=36), nullable=False, server_default=""),
    )
    op.execute("UPDATE refresh_tokens SET familia_id = jti")
    op.create_index("ix_refresh_tokens_familia_id", "refresh_tokens", ["familia_id"])


def downgrade() -> None:
    op.drop_index("ix_refresh_tokens_familia_id", table_name="refresh_tokens")
    op.drop_column("refresh_tokens", "familia_id")
    op.drop_column("usuarios", "token_version")
    op.drop_column("usuarios", "bloqueado_hasta")
    op.drop_column("usuarios", "intentos_fallidos")