"""
Modelo de usuário com autenticação.

Imports:
- Column, Integer, String, Boolean, DateTime: tipos de coluna do SQLAlchemy.
  Cada tipo mapeia para um tipo SQL (String → VARCHAR, Integer → INT, etc).

- func: funções SQL do SQLAlchemy. func.now() gera CURRENT_TIMESTAMP
  no banco — a data é gerada pelo PostgreSQL, não pelo Python.

- Enum (Python): define valores fixos para role.
  No banco, role só aceita 'admin', 'gestor' ou 'analista'.

Por que 3 perfis?
- admin: gerencia usuários, configura sistema, vê tudo
- gestor: vê dashboard, gera relatórios do seu setor
- analista: consulta dados, exporta CSV, sem acesso a config
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="analista")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"