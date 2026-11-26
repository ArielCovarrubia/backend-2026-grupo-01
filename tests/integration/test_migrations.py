import os
import subprocess
import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine, inspect

ROOT = Path(__file__).resolve().parents[2]


def _alembic(database_url: str, *args: str) -> None:
    subprocess.run(
        [sys.executable, "-m", "alembic", *args],
        env={**os.environ, "DATABASE_URL": database_url},
        cwd=ROOT,
        check=True,
    )


def _columns(database_url: str, table: str) -> set[str]:
    engine = create_engine(database_url)
    try:
        return {column["name"] for column in inspect(engine).get_columns(table)}
    finally:
        engine.dispose()


@pytest.mark.integration
def test_account_security_migration_upgrades_and_downgrades(tmp_path):
    database_url = f"sqlite:///{tmp_path}/migrations.db"
    new_columns = {"intentos_fallidos", "bloqueado_hasta", "token_version"}

    _alembic(database_url, "upgrade", "head")
    assert new_columns <= _columns(database_url, "usuarios")
    assert "familia_id" in _columns(database_url, "refresh_tokens")

    _alembic(database_url, "downgrade", "2a8b7c9d0e1f")
    assert not new_columns & _columns(database_url, "usuarios")
    assert "familia_id" not in _columns(database_url, "refresh_tokens")

    _alembic(database_url, "upgrade", "head")
    assert new_columns <= _columns(database_url, "usuarios")