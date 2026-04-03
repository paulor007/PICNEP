# tests/test_cost_engine.py

"""Testes unitários do motor de custo real — coração do PICNEP."""

import pytest
from unittest.mock import Mock
from analysis.cost_engine import calcular_custo_real, _extrair_dias_pagamento

# ── Fixtures ──

def make_quote(**overrides):
    """Cria um Quote mock com valores padrão sensíveis."""
    defaults = {
        "id": 1,
        "item_id": 1,
        "supplier_id": 1,
        "unit_price": 100.0,
        "quantity": 10,
        "freight": 50.0,
        "payment_term": "à vista",   # ← SEM 's' — singular, igual ao model
        "delivery_days": 7,
    }
    defaults.update(overrides)
    return Mock(**defaults)

# ── Testes de calcular_custo_real ──

class TestCalcularCustoReal:

    def test_custo_basico_a_vista(self):
        """À vista sem frete sem espera: custo real = preço × quantidade."""
        quote = make_quote(
            unit_price=48, quantity=100, freight=0,
            payment_term="à vista",   # ← SEM 's'
            delivery_days=0,          # ← Sem espera para teste puro
        )
        resultado = calcular_custo_real(quote)

        assert resultado["custo_produto"] == 4800.0
        assert resultado["custo_frete"] == 0.0
        assert resultado["custo_bruto"] == 4800.0
        assert resultado["beneficio_prazo"] == 0.0
        assert resultado["dias_pagamento"] == 0
        # Sem espera e sem prazo → custo_real = custo_bruto
        assert resultado["custo_real"] == 4800.0

    def test_beneficio_prazo_30_dias(self):
        """30 dias de prazo dá 2% de benefício (taxa padrão)."""
        quote = make_quote(
            unit_price=46, quantity=100, freight=200,
            payment_term="30 dias",   # ← SEM 's'
            delivery_days=0,          # ← Sem espera para isolar o teste do prazo
        )
        resultado = calcular_custo_real(quote)

        custo_bruto = 46 * 100 + 200  # 4800
        beneficio = custo_bruto * 0.02 * (30 / 30)  # 96.0
        custo_real_esperado = custo_bruto - beneficio  # 4704.0

        assert resultado["custo_bruto"] == custo_bruto
        assert resultado["beneficio_prazo"] == beneficio
        assert resultado["custo_real"] == pytest.approx(custo_real_esperado, abs=0.01)

    def test_custo_espera_delivery_days(self):
        """delivery_days adiciona custo de espera ao custo real."""
        sem_espera = make_quote(delivery_days=0, payment_term="à vista")
        com_espera = make_quote(delivery_days=10, payment_term="à vista")

        r1 = calcular_custo_real(sem_espera)
        r2 = calcular_custo_real(com_espera)

        # Com espera deve custar mais
        assert r2["custo_real"] > r1["custo_real"]
        # Diferença = custo_bruto * 0.005 * 10 dias
        custo_bruto = 100.0 * 10 + 50.0  # 1050
        espera_esperada = custo_bruto * 0.005 * 10  # 52.5
        assert r2["custo_real"] - r1["custo_real"] == pytest.approx(espera_esperada, abs=0.01)

    def test_comparacao_fornecedor_a_vs_b(self):
        """Fornecedor A (caro, à vista, rápido) vs B (barato, 30 dias, lento)."""
        quote_a = make_quote(
            unit_price=48, quantity=100, freight=0,
            payment_term="à vista", delivery_days=3,
        )
        quote_b = make_quote(
            unit_price=46, quantity=100, freight=200,
            payment_term="30 dias", delivery_days=5,
        )

        custo_a = calcular_custo_real(quote_a)
        custo_b = calcular_custo_real(quote_b)

        # B tem benefício do prazo (30 dias) que compensa o frete
        # Verificar que B é mais barato que A
        assert custo_b["custo_real"] < custo_a["custo_real"]

    def test_taxa_capital_customizada(self):
        """Taxa de capital diferente do padrão 2%."""
        quote = make_quote(unit_price=100, quantity=10, freight=0, payment_term="30 dias")

        resultado_2pct = calcular_custo_real(quote, taxa_capital=0.02)
        resultado_5pct = calcular_custo_real(quote, taxa_capital=0.05)

        # Maior taxa = maior benefício do prazo = menor custo real
        assert resultado_5pct["custo_real"] < resultado_2pct["custo_real"]

    def test_quantidade_zero_nao_causa_divisao_por_zero(self):
        """Proteção contra divisão por zero."""
        quote = make_quote(quantity=0)
        resultado = calcular_custo_real(quote)
        assert resultado["custo_unitario_real"] == 0

    def test_frete_incluso_no_custo_bruto(self):
        """Frete deve ser somado ao custo bruto."""
        sem_frete = make_quote(freight=0)
        com_frete = make_quote(freight=500)

        r1 = calcular_custo_real(sem_frete)
        r2 = calcular_custo_real(com_frete)

        assert r2["custo_bruto"] - r1["custo_bruto"] == 500

    def test_custo_unitario_real_calculado_corretamente(self):
        """Custo unitário real = custo_real / quantidade."""
        quote = make_quote(unit_price=100, quantity=10, freight=0, payment_term="à vista")
        resultado = calcular_custo_real(quote)
        assert resultado["custo_unitario_real"] == pytest.approx(
            resultado["custo_real"] / 10, abs=0.001
        )


# ── Testes de _extrair_dias_pagamento ──

class TestExtrairDiasPagamento:

    def test_a_vista(self):
        assert _extrair_dias_pagamento("à vista") == 0

    def test_a_vista_uppercase(self):
        assert _extrair_dias_pagamento("À Vista") == 0

    def test_30_dias(self):
        assert _extrair_dias_pagamento("30 dias") == 30

    def test_60_dias(self):
        assert _extrair_dias_pagamento("60 dias") == 60

    def test_string_vazia(self):
        assert _extrair_dias_pagamento("") == 0

    def test_none(self):
        assert _extrair_dias_pagamento(None) == 0

    def test_formato_diferente(self):
        """Aceita variações como '30/60/90 dias'."""
        assert _extrair_dias_pagamento("30/60/90 dias") == 30