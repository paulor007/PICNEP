"""
Seed — Popula o banco com dados demo da Construtora Horizonte.

Roda: python data/seed.py
Idempotente: pode rodar múltiplas vezes sem duplicar dados.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import random
from datetime import date, timedelta

from core.database import SessionLocal, engine, Base
from core.security import hash_password
from models.user import User
from models.supplier import Supplier
from models.item import Item
from models.quote import Quote
from models.purchase import Purchase
from models.alert import Alert

random.seed(42)


def seed():
    """Popula banco com dados demo."""
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Verificar se já tem dados (idempotente)
        existing_users = db.query(User).count()
        if existing_users > 0:
            print("⚠️  Banco já tem dados. Limpando para recriar...")

        # Limpar dados antigos (ordem importa por foreign keys)
        db.query(Alert).delete()
        db.query(Purchase).delete()
        db.query(Quote).delete()
        db.query(Item).delete()
        db.query(Supplier).delete()
        db.query(User).delete()
        db.commit()

        # ── USUÁRIOS ──
        users = [
            User(
                name="Paulo Lavarini",
                email="paulo@construtora.com",
                password_hash=hash_password("senha123"),
                role="admin",
            ),
            User(
                name="Visitante Demo",
                email="demo@picnep.com",
                password_hash=hash_password("demo123"),
                role="gestor",
            ),
        ]
        db.add_all(users)
        db.flush()
        print(f"  {len(users)} usuários criados")

        # ── FORNECEDORES ──
        fornecedores = [
            Supplier(name="Materiais BH Ltda", city="Belo Horizonte", state="MG",
                     contact_name="João Silva", avg_delivery_days=5, payment_terms="30 dias"),
            Supplier(name="Constrular MG", city="Contagem", state="MG",
                     contact_name="Maria Santos", avg_delivery_days=3, payment_terms="à vista"),
            Supplier(name="DepMat Betim", city="Betim", state="MG",
                     contact_name="Carlos Souza", avg_delivery_days=7, payment_terms="28/56 dias"),
            Supplier(name="Casa do Construtor", city="Belo Horizonte", state="MG",
                     contact_name="Ana Costa", avg_delivery_days=4, payment_terms="30 dias"),
            Supplier(name="Ferreira Materiais", city="Santa Luzia", state="MG",
                     contact_name="Pedro Ferreira", avg_delivery_days=6, payment_terms="à vista"),
            Supplier(name="MG Construções", city="Ribeirão das Neves", state="MG",
                     contact_name="Lucas Mendes", avg_delivery_days=8, payment_terms="30/60 dias"),
        ]
        db.add_all(fornecedores)
        db.flush()
        print(f"  {len(fornecedores)} fornecedores criados")

        # ── ITENS ──
        itens = [
            Item(name="Cimento CP-II 50kg", category="Material", unit="saco"),
            Item(name="Argamassa AC-III 20kg", category="Material", unit="saco"),
            Item(name="Brita nº1 m³", category="Material", unit="m³"),
            Item(name="Bloco Cerâmico 14x19x39", category="Material", unit="un"),
            Item(name="Aço CA-50 10mm", category="Material", unit="kg"),
            Item(name="Areia Média m³", category="Material", unit="m³"),
            Item(name="Tinta Acrílica 18L", category="Acabamento", unit="lata"),
            Item(name="Tubo PVC 100mm 6m", category="Hidráulica", unit="un"),
        ]
        db.add_all(itens)
        db.flush()
        print(f"  {len(itens)} itens criados")

        # ── COTAÇÕES ──
        precos_base = [48.0, 22.0, 95.0, 1.85, 8.50, 85.0, 320.0, 45.0]

        cotacoes = []
        for idx, item in enumerate(itens):
            preco_base = precos_base[idx]
            for supplier in fornecedores:
                variacao = random.uniform(-0.15, 0.15)
                preco = round(preco_base * (1 + variacao), 2)
                frete = round(random.choice([0, 50, 100, 150, 200]), 2)
                qtd = random.choice([50, 100, 200, 500, 1000])
                dias_atras = random.randint(0, 60)

                cotacoes.append(Quote(
                    item_id=item.id,
                    supplier_id=supplier.id,
                    unit_price=preco,
                    freight=frete,
                    delivery_days=supplier.avg_delivery_days,
                    payment_term=supplier.payment_terms,
                    quantity=qtd,
                    total_cost=round((preco * qtd) + frete, 2),
                    date=date.today() - timedelta(days=dias_atras),
                ))

        db.add_all(cotacoes)
        db.flush()
        print(f"  {len(cotacoes)} cotações criadas")

        # ── COMPRAS ──
        compras = []
        for _ in range(18):
            item = random.choice(itens)
            supplier = random.choice(fornecedores)
            idx = itens.index(item)
            preco_base = precos_base[idx]
            preco = round(preco_base * random.uniform(0.9, 1.1), 2)
            qtd = random.choice([50, 100, 200])
            frete = round(random.choice([0, 80, 150]), 2)
            dias_atras = random.randint(5, 90)

            compras.append(Purchase(
                item_id=item.id,
                supplier_id=supplier.id,
                date=date.today() - timedelta(days=dias_atras),
                quantity=qtd,
                unit_price=preco,
                freight=frete,
                total_cost=round((preco * qtd) + frete, 2),
                payment_term=supplier.payment_terms,
                status="concluida",
            ))

        db.add_all(compras)
        db.commit()
        print(f"  {len(compras)} compras criadas")

        print("\n  Banco populado com sucesso!")
        print("  Admin: paulo@construtora.com / senha123")
        print("  Gestor: demo@picnep.com / demo123")

    except Exception as e:
        db.rollback()
        print(f"  Erro: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()