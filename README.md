# PICNEP — Inteligência de Compras para PMEs

> **O Custo da Indecisão:** PMEs não perdem dinheiro só pagando caro — perdem porque não sabem _quando_ comprar. Compram por "susto" (estoque acabou) ou intuição. O PICNEP muda isso.

![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-API_REST-009688?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql)
![JWT](https://img.shields.io/badge/Auth-JWT+RBAC-orange)
![Docker](https://img.shields.io/badge/Docker-Container-2496ED?logo=docker)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?logo=streamlit)
![Status](https://img.shields.io/badge/Status-Conclu%C3%ADdo-brightgreen)

---

## O Problema

PMEs brasileiras perdem margem de lucro porque:

- Cotam de forma desorganizada (email, WhatsApp, planilha avulsa)
- Não comparam o **Custo Efetivo Total** (preço + frete + prazo de pagamento)
- Não têm histórico para saber se estão pagando mais caro que antes
- Não sabem quando renegociar — compram quando o estoque acaba

## A Solução

Engine de análise que centraliza cotações e histórico de compras, calcula o **Custo Efetivo Total** de cada fornecedor e gera recomendações acionáveis: **comprar agora, esperar ou renegociar** — baseadas em dados reais, não intuição.

O sistema gera ROI direto: se paga na primeira economia sugerida.

---

## Caso Real Demonstrável

**Cenário:** Construtora Horizonte (PME de BH) precisa comprar 100 sacos de Cimento CP-II.
Recebeu 3 cotações:

| Fornecedor    | Preço/un | Frete  | Prazo Pgto | Custo Efetivo (100un) |
| ------------- | -------- | ------ | ---------- | --------------------- |
| Materiais BH  | R$ 48,50 | R$ 150 | 30 dias    | **R$ 4.853,00**       |
| Constrular MG | R$ 52,00 | R$ 0   | à vista    | R$ 5.200,00           |
| DepMat Betim  | R$ 46,90 | R$ 200 | 28/56 dias | **R$ 4.796,60**       |

### O que o PICNEP recomenda:

> **COMPRAR AGORA — DepMat Betim** tem o menor Custo Efetivo Total (R$ 4.796,60).
>
> O preço unitário não é o menor, mas o prazo de pagamento 28/56 dias compensa: capital de giro fica livre por mais tempo. É o melhor custo-benefício real.
>
> **Economia vs fornecedor mais caro: R$ 403,40 neste pedido.**
> Em 12 meses com compras mensais: **R$ 4.840,80 de economia anual.**

_O comprador que olha só preço unitário escolheria DepMat. O comprador que olha Custo Efetivo Total TAMBÉM escolhe DepMat — mas pelo motivo certo._

---

## Números do Projeto

| Métrica            | Valor                                            |
| ------------------ | ------------------------------------------------ |
| Endpoints API      | 25+ (documentados no Swagger)                    |
| Tabelas PostgreSQL | 6 (User, Supplier, Item, Quote, Purchase, Alert) |
| Engine de análise  | 3 módulos (CET, oportunidades, recomendação)     |
| Testes Pytest      | 9+ (auth, CRUD, análise)                         |
| Perfis RBAC        | 3 (admin, gestor, analista)                      |
| Dashboard          | 5 abas + 2 modos (API + demo)                    |
| Credenciais demo   | 2 (admin + gestor)                               |

---

## Arquitetura

```
  Dashboard (Streamlit) ──HTTP──> FastAPI (25+ endpoints) ──> PostgreSQL
        │                              ↕
        │                      Engine de Análise
        │                   ┌──────────┼──────────┐
        │                   ▼          ▼          ▼
        │              Custo Real  Oportunidades  Recomendação
        │              (CET)       (economia)     (comprar/esperar)
        │
        └── Modo Demo: acessa banco direto (portfolio/deploy)
```

```
picnep/
├── main.py                      ← FastAPI (25+ endpoints)
├── dashboard.py                 ← Streamlit (dual-mode)
├── docker-compose.yml           ← API + PostgreSQL
├── Dockerfile
├── api/
│   ├── auth/router.py           ← Register, Login, Token (JWT)
│   ├── deps.py                  ← get_current_user, require_role (RBAC)
│   └── routes/
│       ├── suppliers.py         ← CRUD fornecedores (5 endpoints)
│       ├── items.py             ← CRUD itens (5 endpoints)
│       ├── quotes.py            ← Upload planilha + comparação (4 endpoints)
│       ├── purchases.py         ← Histórico compras (3 endpoints)
│       ├── analysis.py          ← CET, oportunidades, recomendação (5 endpoints)
│       ├── alerts.py            ← Alertas inteligentes (2 endpoints)
│       └── users.py             ← Gestão de usuários — admin (5 endpoints)
├── analysis/
│   ├── cost_engine.py           ← Custo Efetivo Total (preço+frete+prazo)
│   ├── opportunity_detector.py  ← Detecta economia potencial
│   └── recommendation.py       ← Comprar agora / esperar / renegociar
├── models/ (6 tabelas SQLAlchemy)
├── schemas/ (validação Pydantic)
├── core/ (config, database, security)
├── data/seed.py (dados demo: 2 users, 6 fornecedores, 8 itens, 48 cotações, 18 compras)
└── tests/ (auth, suppliers, analysis)
```

---

## Perfis de Acesso (RBAC)

| Perfil          | Permissões                                             |
| --------------- | ------------------------------------------------------ |
| 🔴 **Admin**    | Tudo: gerenciar usuários, CRUD, análises, configuração |
| 🟡 **Gestor**   | Dashboard, cotações, relatórios, recomendações         |
| 🟢 **Analista** | Consultar dados, exportar, ver alertas                 |

O admin gerencia perfis pela aba Admin do dashboard ou via API.

---

## Stack Técnica

| Tech                         | Para quê          | Por quê                                                 |
| ---------------------------- | ----------------- | ------------------------------------------------------- |
| **FastAPI**                  | API REST backend  | Mais moderna que Flask, async, docs Swagger automáticas |
| **PostgreSQL 16**            | Banco de produção | Multi-usuário, robusto, padrão indústria                |
| **SQLAlchemy 2.0 + Alembic** | ORM + migrações   | Versionamento do banco como git                         |
| **JWT + bcrypt**             | Autenticação      | Token stateless + hash seguro                           |
| **Pydantic**                 | Validação         | Schemas entrada/saída, 422 automático                   |
| **Pandas**                   | Engine de análise | Cálculo de CET e oportunidades                          |
| **Streamlit + Plotly**       | Dashboard         | Interface portfolio com gráficos interativos            |
| **Docker**                   | Container         | Deploy com um comando                                   |
| **Pytest**                   | Testes            | API + regras de negócio                                 |

---

## Como Rodar

```bash
# 1. Clone
git clone https://github.com/paulor007/picnep.git
cd picnep

# 2. Ambiente
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt

# 3. Banco (Docker)
docker-compose up -d

# 4. Migrações + seed
alembic upgrade head
python data/seed.py

# 5. API (Terminal 1)
uvicorn main:app --reload
# → http://localhost:8000/docs (Swagger)

# 6. Dashboard (Terminal 2, ou sozinho em modo demo)
streamlit run dashboard.py
# → http://localhost:8502
```

### Docker completo (API + banco):

```bash
docker-compose up --build -d
# API: http://localhost:8000/docs
# Dashboard: streamlit run dashboard.py
```

---

## Credenciais Demo

| Perfil | Email                 | Senha    |
| ------ | --------------------- | -------- |
| Admin  | paulo@construtora.com | senha123 |
| Gestor | demo@picnep.com       | demo123  |

---

## Endpoints Principais

```
POST   /auth/register                   → Criar conta
POST   /auth/token                      → Login (JWT)

GET    /api/v1/suppliers                 → Listar fornecedores
POST   /api/v1/suppliers                 → Cadastrar fornecedor
POST   /api/v1/quotes/upload             → Upload planilha de cotações
GET    /api/v1/quotes/compare/{item_id}  → Comparar fornecedores

GET    /api/v1/analysis/cost/{item_id}         → Ranking Custo Efetivo Total
GET    /api/v1/analysis/opportunities          → Oportunidades de economia
GET    /api/v1/analysis/recommendations        → Comprar / esperar / renegociar
GET    /api/v1/analysis/recommendations/{id}   → Recomendação por item
POST   /api/v1/analysis/alerts/generate        → Gerar alertas

GET    /api/v1/users                     → Listar usuários (admin)
POST   /api/v1/users                     → Criar usuário (admin)
PUT    /api/v1/users/{id}/role           → Alterar perfil (admin)
```

Documentação Swagger completa: `http://localhost:8000/docs`

---

## Desafios Técnicos Resolvidos

| Desafio                               | Solução                                              |
| ------------------------------------- | ---------------------------------------------------- |
| Preço unitário ≠ custo real           | Engine de CET: preço × qtd + frete − benefício prazo |
| Fornecedor "barato" com frete caro    | Ranking por custo real, não por preço                |
| Dashboard sem API rodando             | Dual-mode: detecta API, senão acessa banco direto    |
| Visitante do portfolio precisa testar | Seed com dados demo + credenciais prontas            |
| Swagger 422 no login                  | Endpoint `/auth/token` com OAuth2PasswordRequestForm |
| passlib + bcrypt incompatível         | Pin bcrypt==4.0.1 no Python 3.13                     |
| seed.py ForeignKey violation          | IDs dinâmicos (item.id) em vez de hardcoded (1-8)    |

---

## Roadmap

- [x] API REST com FastAPI (25+ endpoints)
- [x] PostgreSQL + Alembic (6 tabelas versionadas)
- [x] Autenticação JWT + RBAC (3 perfis)
- [x] Upload de cotações (Excel/CSV)
- [x] Engine de Custo Efetivo Total
- [x] Detector de oportunidades
- [x] Recomendação: comprar / esperar / renegociar
- [x] Dashboard Streamlit (5 abas + dual-mode)
- [x] Gestão de usuários (admin)
- [x] Seed com dados demo
- [x] Testes (auth, CRUD, análise)
- [x] Docker (API + banco)
- [ ] Deploy Streamlit Cloud
- [ ] Integração com NF-e / XML fiscal
- [ ] Sazonalidade automática por item
- [ ] Export PDF de relatório de compras
- [ ] Mobile (React Native consumindo API)

---

## Código-fonte

Repositório privado. Acesso para avaliação técnica sob demanda.

[Portfolio](https://paulolavarini-portfolio.netlify.app) | [GitHub](https://github.com/paulor007)

---

## Autor

**Paulo Lavarini** — Desenvolvedor Python

[![Portfolio](https://img.shields.io/badge/Portfolio-Netlify-00C7B7?logo=netlify)](https://paulolavarini-portfolio.netlify.app)
[![GitHub](https://img.shields.io/badge/GitHub-paulor007-181717?logo=github)](https://github.com/paulor007)
