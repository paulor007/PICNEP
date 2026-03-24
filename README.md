# PICNEP — Inteligência de Compras para PMEs

> **SaaS que calcula o Custo Efetivo Total de compras, compara fornecedores
> e recomenda: comprar agora, esperar ou renegociar.**

![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-API_REST-009688?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql)
![JWT](https://img.shields.io/badge/Auth-JWT+RBAC-orange)
![Docker](https://img.shields.io/badge/Docker-Container-2496ED?logo=docker)

---

## O Problema

PMEs brasileiras perdem margem de lucro porque:

- Cotam de forma desorganizada (email, WhatsApp, PDF)
- Não comparam o **custo real** (preço + frete + prazo de pagamento)
- Não sabem quando renegociar
- Não têm histórico para tomar decisão

## A Solução

Engine de análise que calcula o **Custo Efetivo Total**, detecta
oportunidades de economia e gera recomendações acionáveis baseadas
em dados históricos.

---

## Caso Real Demonstrável

**Item:** Cimento CP-II 50kg | **Quantidade:** 100 sacos | **3 fornecedores:**

| Fornecedor    | Preço/un | Frete  | Prazo Pgto | CET (100un)     |
| ------------- | -------- | ------ | ---------- | --------------- |
| Materiais BH  | R$ 48,50 | R$ 150 | 30 dias    | **R$ 4.853,00** |
| Constrular MG | R$ 52,00 | R$ 0   | à vista    | R$ 5.200,00     |
| DepMat Betim  | R$ 46,90 | R$ 200 | 28/56 dias | **R$ 4.796,60** |

### Recomendação do PICNEP:

> **COMPRAR AGORA** — DepMat Betim tem o menor Custo Efetivo Total
> (R$ 4.796,60). Embora o preço unitário não seja o menor, o prazo de
> pagamento 28/56 dias compensa: capital de giro fica livre por mais tempo.
>
> **Economia vs fornecedor mais caro: R$ 403,40 neste pedido.**
> Em 12 meses com compras mensais: **R$ 4.840,80 de economia.**

---

## Arquitetura

Dashboard (Streamlit) ──HTTP──> FastAPI ──> PostgreSQL
↕
Engine de Análise
(CET + Oportunidades + Recomendação)

picnep/
├── main.py ← FastAPI (20+ endpoints)
├── dashboard.py ← Streamlit (dual-mode: API ou demo)
├── docker-compose.yml ← PostgreSQL container
├── api/
│ ├── auth/router.py ← Register, Login (JWT)
│ └── routes/
│ ├── suppliers.py ← CRUD fornecedores
│ ├── items.py ← CRUD itens
│ ├── quotes.py ← Upload + comparação cotações
│ ├── purchases.py ← Histórico compras
│ ├── analysis.py ← CET, oportunidades, recomendação
│ ├── alerts.py ← Alertas inteligentes
│ └── users.py ← Gestão de usuários (admin)
├── analysis/
│ ├── cost_engine.py ← Custo Efetivo Total
│ ├── opportunity_detector.py ← Economia potencial
│ └── recommendation.py ← Comprar / esperar / renegociar
├── models/ (6 tabelas)
├── schemas/ (validação Pydantic)
├── core/ (config, database, security)
└── tests/

## Perfis de Acesso (RBAC)

| Perfil       | Permissões                                             |
| ------------ | ------------------------------------------------------ |
| **Admin**    | Tudo: gerenciar usuários, CRUD, análises, configuração |
| **Gestor**   | Dashboard, cotações, relatórios, recomendações         |
| **Analista** | Consultar dados, exportar, ver alertas                 |

## Tecnologias

| Tech                 | Para quê                              |
| -------------------- | ------------------------------------- |
| FastAPI              | API REST com docs Swagger automáticas |
| PostgreSQL 16        | Banco de produção                     |
| SQLAlchemy + Alembic | ORM + migrações versionadas           |
| JWT + bcrypt         | Autenticação stateless + hash seguro  |
| Pandas               | Engine de análise de custo            |
| Streamlit + Plotly   | Dashboard interativo                  |
| Docker               | Container para banco                  |
| Pytest               | Testes de API + regras de negócio     |

## Como rodar

```bash
# 1. Clone e configure
git clone https://github.com/paulor007/picnep.git
cd picnep
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt

# 2. Banco PostgreSQL (Docker)
docker-compose up -d

# 3. Migrações
alembic upgrade head

# 4. Dados demo
python data/seed.py

# 5. API (Terminal 1)
uvicorn main:app --reload
# → Swagger: http://localhost:8000/docs

# 6. Dashboard (Terminal 2, ou sozinho em modo demo)
streamlit run dashboard.py
# → http://localhost:8502
```

## Credenciais Demo

| Perfil | Email                 | Senha    |
| ------ | --------------------- | -------- |
| Admin  | paulo@construtora.com | senha123 |
| Gestor | demo@picnep.com       | demo123  |

## Endpoints Principais

POST /auth/register → Criar conta
POST /auth/token → Login (JWT)
GET /api/v1/suppliers → Fornecedores
POST /api/v1/quotes/upload → Upload planilha cotações
GET /api/v1/quotes/compare/{id} → Comparar fornecedores
GET /api/v1/analysis/cost/{id} → Ranking CET
GET /api/v1/analysis/opportunities → Economia potencial
GET /api/v1/analysis/recommendations → Comprar/esperar/renegociar
GET /api/v1/users → Listar usuários (admin)
PUT /api/v1/users/{id}/role → Alterar perfil (admin)

## 👨‍💻 Autor

**Paulo Lavarini** — [Portfolio](https://paulolavarini-portfolio.netlify.app) | [GitHub](https://github.com/paulor007)
