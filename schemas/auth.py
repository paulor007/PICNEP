"""
Schemas de autenticação — login, registro e token.

Por que schemas separados para auth?
- RegisterRequest tem 'name' e 'password' (texto puro)
- LoginRequest tem só 'email' e 'password'
- TokenResponse retorna o token (nunca a senha)
- UserResponse retorna dados do usuário (sem password_hash)
"""

from datetime import datetime
from pydantic import BaseModel, Field

class RegisterRequest(BaseModel):
    """Dados para criar conta."""
    name: str = Field(..., min_length=2, max_length=100, examples=["Paulo Lavarini"])
    email: str = Field(..., examples=["paulo@construtora.com"])
    password: str = Field(..., min_length=6, max_length=100, examples=["senha123"])
    role: str = Field("analista", examples=["admin", "gestor", "analista"])

class LoginRequest(BaseModel):
    """Dados para fazer login."""
    email: str = Field(..., examples=["paulo@construtora.com"])
    password: str = Field(..., examples=["senha123"])

class TokenResponse(BaseModel):
    """Resposta do login — token JWT."""
    access_token: str
    token_type: str = "bearer"
    role: str
    name: str

class UserResponse(BaseModel):
    """Dados do usuário (sem senha)."""
    id: int
    name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
