"""
Configurações centralizadas do PICNEP.

Usa Pydantic BaseSettings v2 com model_config.
Lê variáveis do .env automaticamente com validação de tipos.
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações carregadas do .env com validação automática."""

    # Banco
    DATABASE_URL: str = "postgresql://neondb_owner:npg_oT4I7tacuJBD@ep-lucky-credit-acetl9br.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

    # JWT
    SECRET_KEY: str = "14F264kn@picnep.com"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Empresa
    EMPRESA_NOME: str = "Construtora Horizonte"

    # Diretórios
    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = Path(__file__).parent.parent / "data"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


# Instância global
settings = Settings()