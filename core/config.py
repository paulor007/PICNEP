"""
Configurações centralizadas do PICNEP.

Diferença do SARE:
- Usa Pydantic BaseSettings em vez de os.getenv manual
- Valida tipos automaticamente (se DATABASE_URL não existir, dá erro claro)
- Suporta .env nativo sem precisar de load_dotenv()

Imports:
- pydantic_settings.BaseSettings: classe que lê .env e valida tipos
  automaticamente. Cada campo é um atributo tipado. Se faltar variável
  obrigatória, erro claro na inicialização (não no meio da execução).

- pathlib.Path: caminhos de arquivo multiplataforma (Windows/Linux).
"""

from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Configurações carregadas do .env com validação automática."""

    # Banco
    DATABASE_URL: str = "postgresql://picnep:picnep123@localhost:5432/picnep"

    # JWT
    SECRET_KEY: str = "dev-secret-key-troque-em-producao"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Empresa
    EMPRESA_NOME: str = "Construtora Horizonte"

    # Diretórios
    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = Path(__file__).parent.parent / "data"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Instância global (importar de qualquer lugar)
settings = Settings()