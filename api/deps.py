"""
Dependências compartilhadas entre rotas.

Imports:
- Depends: mecanismo do FastAPI para injeção de dependência.
  Em vez de criar sessão manual dentro de cada endpoint,
  o FastAPI chama get_db() automaticamente e entrega a sessão.

Como funciona:
  @app.get("/items")
  def list_items(db: Session = Depends(get_db)):
      return db.query(Item).all()

  O FastAPI:
  1. Chama get_db()
  2. Recebe a sessão
  3. Passa para 'db' no endpoint
  4. Quando o endpoint retorna, fecha a sessão (finally)
"""

from core.database import get_db

# Re-exporta para imports limpos
__all__ = ["get_db"]