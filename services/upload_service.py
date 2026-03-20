"""
Serviço de upload e processamento de planilhas de cotação.

Imports:
- UploadFile (FastAPI): arquivo enviado (.filename, .read())
- io.BytesIO: transforma bytes em "arquivo virtual" para o Pandas ler

Fluxo: usuário manda planilha → Pandas lê → valida → calcula total_cost → salva
"""

import io
from datetime import date

import pandas as pd
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

from models.item import Item
from models.supplier import Supplier
from models.quote import Quote


# Mapeamento de nomes aceitos → padrão interno
COLUMN_MAP = {
    "item": "item_id", "produto": "item_id", "material": "item_id",
    "supplier": "supplier_id", "fornecedor": "supplier_id", "fornecedor_id": "supplier_id",
    "preco": "unit_price", "preco_unitario": "unit_price", "price": "unit_price",
    "valor": "unit_price", "valor_unitario": "unit_price",
    "frete": "freight", "prazo": "delivery_days", "prazo_entrega": "delivery_days",
    "dias": "delivery_days", "pagamento": "payment_term", "condicao": "payment_term",
    "condicao_pagamento": "payment_term", "quantidade": "quantity", "qty": "quantity",
    "data": "date", "data_cotacao": "date", "obs": "notes", "observacao": "notes",
}


def _normalizar_colunas(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    df = df.rename(columns={k: v for k, v in COLUMN_MAP.items() if k in df.columns})
    return df


def processar_upload_cotacoes(
    file: UploadFile,
    db: Session,
    default_date: date | None = None,
) -> dict:
    """
    Processa planilha de cotações e salva no banco.

    Retorna: total_linhas, importadas, erros (por linha)
    """
    content = file.file.read()
    filename = file.filename or "upload"

    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(content))
        elif filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(io.BytesIO(content), engine="openpyxl")
        else:
            raise HTTPException(status_code=400, detail="Use .xlsx ou .csv")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao ler: {e}")

    if df.empty:
        raise HTTPException(status_code=400, detail="Arquivo vazio")

    df = _normalizar_colunas(df)

    required = ["item_id", "supplier_id", "unit_price"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Colunas obrigatórias ausentes: {missing}. Encontradas: {list(df.columns)}"
        )

    importadas = 0
    erros = []
    use_date = default_date or date.today()

    valid_items = {i.id for i in db.query(Item.id).all()}
    valid_suppliers = {s.id for s in db.query(Supplier.id).all()}

    for idx, row in df.iterrows():
        line_num = idx + 2
        try:
            item_id = int(row["item_id"])
            supplier_id = int(row["supplier_id"])
            unit_price = float(row["unit_price"])

            if item_id not in valid_items:
                erros.append({"linha": line_num, "erro": f"Item {item_id} não existe"})
                continue
            if supplier_id not in valid_suppliers:
                erros.append({"linha": line_num, "erro": f"Fornecedor {supplier_id} não existe"})
                continue
            if unit_price <= 0:
                erros.append({"linha": line_num, "erro": "Preço deve ser > 0"})
                continue

            freight = float(row.get("freight", 0) or 0)
            quantity = int(row.get("quantity", 1) or 1)
            delivery_days = int(row.get("delivery_days", 7) or 7)
            payment_term = str(row.get("payment_term", "à vista") or "à vista")
            notes = str(row["notes"]) if "notes" in row and pd.notna(row.get("notes")) else None
            total_cost = round((unit_price * quantity) + freight, 2)

            quote = Quote(
                item_id=item_id, supplier_id=supplier_id, unit_price=unit_price,
                freight=freight, delivery_days=delivery_days, payment_term=payment_term,
                min_quantity=1, quantity=quantity, total_cost=total_cost,
                date=use_date, notes=notes,
            )
            db.add(quote)
            importadas += 1
        except (ValueError, TypeError) as e:
            erros.append({"linha": line_num, "erro": f"Dados inválidos: {e}"})

    db.commit()
    return {"total_linhas": len(df), "importadas": importadas, "erros": erros}