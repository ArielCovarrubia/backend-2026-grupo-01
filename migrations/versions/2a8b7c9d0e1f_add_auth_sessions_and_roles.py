"""add roles, refresh sessions and password reset tokens

Revision ID: 2a8b7c9d0e1f
Revises: 011c3555b77c
"""

from alembic import op
import sqlalchemy as sa


revision = "2a8b7c9d0e1f"
down_revision = "011c3555b77c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("usuarios", sa.Column("role", sa.String(length=20), nullable=False, server_default="usuario"))
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("jti", sa.String(length=36), nullable=False, unique=True),
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id"), nullable=False),
        sa.Column("token_hash", sa.String(length=255), nullable=False),
        sa.Column("expira_en", sa.DateTime(), nullable=False),
        sa.Column("revocado_en", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_refresh_tokens_jti", "refresh_tokens", ["jti"], unique=True)
    op.create_index("ix_refresh_tokens_usuario_id", "refresh_tokens", ["usuario_id"])
    op.create_table(
        "password_reset_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("jti", sa.String(length=36), nullable=False, unique=True),
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id"), nullable=False),
        sa.Column("expira_en", sa.DateTime(), nullable=False),
        sa.Column("usado_en", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_password_reset_tokens_jti", "password_reset_tokens", ["jti"], unique=True)
    op.create_index("ix_password_reset_tokens_usuario_id", "password_reset_tokens", ["usuario_id"])


def downgrade() -> None:
    op.drop_index("ix_password_reset_tokens_usuario_id", table_name="password_reset_tokens")
    op.drop_index("ix_password_reset_tokens_jti", table_name="password_reset_tokens")
    op.drop_table("password_reset_tokens")
    op.drop_index("ix_refresh_tokens_usuario_id", table_name="refresh_tokens")
    op.drop_index("ix_refresh_tokens_jti", table_name="refresh_tokens")
    op.drop_table("refresh_tokens")
    op.drop_column("usuarios", "role")
