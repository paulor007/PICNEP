"""
Configuração do Alembic para migrações.

Imports:
- context: gerencia o contexto de migração (online/offline).
- engine_from_config: cria engine a partir das configs do alembic.ini.

O truque aqui é importar Base.metadata dos nossos modelos.
Assim o Alembic sabe quais tabelas existem e gera migrações automáticas.
"""

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Importa configurações do PICNEP
from core.config import settings
from core.database import Base

# Importa TODOS os modelos (para o Alembic enxergar as tabelas)
from models import User, Supplier, Item, Quote, Purchase, Alert  # noqa: F401

# Configuração do Alembic
config = context.config

# Seta a URL do banco a partir do .env (em vez de hardcoded no alembic.ini)
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata dos modelos (Alembic usa para comparar com o banco real)
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Gera SQL sem conectar ao banco (para review)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Conecta ao banco e aplica migrações."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()