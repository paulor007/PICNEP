"""Testes da lógica de recomendação."""

import pytest
from datetime import date
from tests.conftest import TestSession
from models.item import Item
from models.supplier import Supplier
from models.quote import Quote
from analysis.recommendation import recomendar_item


@pytest.fixture
def db_with_data(setup_db):
    """Banco com dados para teste de recomendação."""
    db = TestSession()
    try:
        # Criar fornecedor e item
        supplier = Supplier(id=1, name="Fornecedor Teste", state="MG", city="BH")
        item = Item(id=1, name="Cimento CP-II", category="Material", unit="saco")
        db.add_all([supplier, item])
        db.commit()

        # Cotação atual
        quote = Quote(
            id=1, item_id=1, supplier_id=1,
            unit_price=45.0, quantity=100, freight=0,
            payment_term="à vista", delivery_days=3,
            total_cost=4500, date=date.today(),
        )
        db.add(quote)
        db.commit()

        yield db
    finally:
        db.close()


class TestRecomendarItem:

    def test_sem_cotacoes_retorna_pedir_cotacao(self, db_with_data):
        """Item sem cotação → ação 'pedir_cotacao'."""
        db = db_with_data
        # Item 999 não existe no banco de cotações
        item = Item(id=999, name="Item Sem Cotação", category="Outro", unit="un")
        db.add(item)
        db.commit()

        result = recomendar_item(db, 999)
        assert result["acao"] == "pedir_cotacao"

    def test_primeira_compra_retorna_comprar_agora(self, db_with_data):
        """Primeira compra (sem histórico) → ação 'comprar_agora'."""
        result = recomendar_item(db_with_data, 1)
        assert result["acao"] == "comprar_agora"
        assert "Primeira compra" in result["motivo"]

    def test_item_inexistente(self, db_with_data):
        """Item que não existe → retorna erro."""
        result = recomendar_item(db_with_data, 9999)
        assert "erro" in result