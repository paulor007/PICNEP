"""
PICNEP — Dashboard de Inteligência de Compras.

Dois modos automáticos:
- Modo API: consome FastAPI via HTTP (quando uvicorn está rodando)
- Modo Demo: acessa banco direto (portfolio / Streamlit Cloud)

Rodar: streamlit run dashboard.py
"""

import streamlit as st
import plotly.graph_objects as go
import requests

# ══════════════════════════════════════════
# DETECTAR MODO (API ou Demo)
# ══════════════════════════════════════════
@st.cache_data(ttl=30)
def check_api():
    try:
        r = requests.get("http://localhost:8000/health", timeout=1)
        return r.status_code == 200
    except Exception:
        return False

API_AVAILABLE = check_api()

if API_AVAILABLE:
    from services.api_client import PicnepClient
else:
    from core.database import SessionLocal
    from core.security import verify_password, hash_password
    from models.user import User
    from models.supplier import Supplier
    from models.item import Item
    from models.quote import Quote
    from models.purchase import Purchase
    from models.alert import Alert
    from analysis.cost_engine import ranking_fornecedores_por_item
    from analysis.opportunity_detector import detectar_oportunidades
    from analysis.recommendation import recomendar_todos


# ══════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════

st.set_page_config(
    page_title="PICNEP — Inteligência de Compras",
    page_icon="🏗️",
    layout="wide",
)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "client" not in st.session_state and API_AVAILABLE:
    st.session_state.client = PicnepClient()
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "user_role" not in st.session_state:
    st.session_state.user_role = ""


# ══════════════════════════════════════════
# TELA DE LOGIN
# ══════════════════════════════════════════

if not st.session_state.logged_in:
    st.markdown("""
    <div style="text-align: center; padding: 60px 0 30px 0;">
        <h1 style="color: #2563eb; font-size: 3rem;">🏗️ PICNEP</h1>
        <p style="color: #94a3b8; font-size: 1.2rem;">
            Plataforma de Inteligência de Compras, Negociação e Economia Potencial
        </p>
        <p style="color: #64748b; font-size: 0.9rem;">
            SaaS de inteligência de compras para PMEs •
            Custo Efetivo Total • Engine de Recomendação
        </p>
    </div>
    """, unsafe_allow_html=True)

    mode_text = "🟢 Modo API (FastAPI rodando)" if API_AVAILABLE else "🟡 Modo Demo (acesso direto ao banco)"
    st.caption(f"Status: {mode_text}")

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.subheader("Login")

        with st.form("login_form"):
            email = st.text_input("Email", value="demo@picnep.com")
            password = st.text_input("Senha", type="password", value="demo123")
            submitted = st.form_submit_button("Entrar", type="primary", use_container_width=True)

        if submitted:
            success = False

            if API_AVAILABLE:
                client = st.session_state.client
                if client.login(email, password):
                    success = True
                    st.session_state.user_name = "Usuário"
                    st.session_state.user_role = "via API"
            else:
                db = SessionLocal()
                try:
                    user = db.query(User).filter(User.email == email).first()
                    if user and verify_password(password, user.password_hash):
                        success = True
                        st.session_state.user_name = user.name
                        st.session_state.user_role = user.role
                finally:
                    db.close()

            if success:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Email ou senha incorretos.")

        st.divider()
        st.caption("**Contas demo:**")
        st.caption("Admin: paulo@construtora.com / senha123")
        st.caption("Gestor: demo@picnep.com / demo123")

    st.stop()


# ══════════════════════════════════════════
# HELPERS: buscar dados (funciona nos 2 modos)
# ══════════════════════════════════════════

def _api_get(endpoint):
    if API_AVAILABLE and "client" in st.session_state:
        return st.session_state.client.get(endpoint)
    return None


def get_suppliers():
    data = _api_get("/api/v1/suppliers")
    if data is not None:
        return data
    db = SessionLocal()
    try:
        return [
            {
                "id": s.id,
                "name": s.name,
                "city": s.city,
                "state": s.state,
                "avg_delivery_days": s.avg_delivery_days,
                "payment_terms": s.payment_terms,
                "rating_score": s.rating_score,
                "is_active": s.is_active,
            }

            for s in db.query(Supplier).filter(Supplier.is_active.is_(True)).all()
        ]
    finally:
        db.close()


def get_items():
    data = _api_get("/api/v1/items")
    if data is not None:
        return data
    db = SessionLocal()
    try:
        return [{"id": i.id, "name": i.name, "category": i.category,
                 "unit": i.unit, "current_avg_price": i.current_avg_price}
                for i in db.query(Item).all()]
    finally:
        db.close()


def get_quotes():
    data = _api_get("/api/v1/quotes")
    if data is not None:
        return data
    db = SessionLocal()
    try:
        return [{"id": q.id, "item_id": q.item_id, "supplier_id": q.supplier_id,
                 "unit_price": q.unit_price, "freight": q.freight,
                 "delivery_days": q.delivery_days, "total_cost": q.total_cost,
                 "date": str(q.date)}
                for q in db.query(Quote).order_by(Quote.date.desc()).all()]
    finally:
        db.close()


def get_purchases():
    data = _api_get("/api/v1/purchases")
    if data is not None:
        return data
    db = SessionLocal()
    try:
        return [{"id": p.id, "item_id": p.item_id, "supplier_id": p.supplier_id,
                 "quantity": p.quantity, "unit_price": p.unit_price,
                 "total_cost": p.total_cost, "date": str(p.date), "status": p.status}
                for p in db.query(Purchase).order_by(Purchase.date.desc()).all()]
    finally:
        db.close()


def get_recommendations():
    if API_AVAILABLE and "client" in st.session_state:
        data = st.session_state.client.get("/api/v1/analysis/recommendations")
        return data.get("recommendations", []) if data else []
    db = SessionLocal()
    try:
        return recomendar_todos(db)
    finally:
        db.close()


def get_opportunities():
    if API_AVAILABLE and "client" in st.session_state:
        data = st.session_state.client.get("/api/v1/analysis/opportunities")
        return data.get("opportunities", []) if data else []
    db = SessionLocal()
    try:
        return detectar_oportunidades(db)
    finally:
        db.close()


def get_cost_ranking(item_id):
    if API_AVAILABLE and "client" in st.session_state:
        data = st.session_state.client.get(f"/api/v1/analysis/cost/{item_id}")
        return data.get("ranking", []) if data else []
    db = SessionLocal()
    try:
        return ranking_fornecedores_por_item(db, item_id)
    finally:
        db.close()


def get_alerts():
    if API_AVAILABLE and "client" in st.session_state:
        data = st.session_state.client.get("/api/v1/alerts")
        return data.get("alerts", []) if data else []
    db = SessionLocal()
    try:
        return [{"id": a.id, "type": a.type, "severity": a.severity,
                 "message": a.message, "data": a.data, "is_read": a.is_read,
                 "created_at": str(a.created_at)}
                for a in db.query(Alert).order_by(Alert.created_at.desc()).limit(50).all()]
    finally:
        db.close()


# ══════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════

st.markdown("""
<div style="background: linear-gradient(135deg, #0b0f19 0%, #131a2b 100%);
    border: 1px solid #1e293b; border-radius: 12px; padding: 24px; margin-bottom: 20px;">
    <h1 style="color: #2563eb; margin: 0; font-size: 1.8rem;">
        🏗️ PICNEP — Inteligência de Compras
    </h1>
    <p style="color: #94a3b8; margin: 6px 0 12px 0;">
        Custo Efetivo Total • Recomendações de Compra • Alertas Inteligentes
    </p>
    <div style="display: flex; gap: 16px; flex-wrap: wrap;">
        <div style="background: #1e293b; padding: 6px 14px; border-radius: 8px;">
            <span style="color: #2563eb; font-weight: bold;">📥 Problema</span>
            <span style="color: #e2e8f0;"> — PMEs compram sem histórico nem comparação real</span>
        </div>
        <div style="background: #1e293b; padding: 6px 14px; border-radius: 8px;">
            <span style="color: #4ade80; font-weight: bold;">✅ Solução</span>
            <span style="color: #e2e8f0;"> — Engine calcula CET e recomenda: comprar, esperar ou renegociar</span>
        </div>
        <div style="background: #1e293b; padding: 6px 14px; border-radius: 8px;">
            <span style="color: #f59e0b; font-weight: bold;">🔌 Integração</span>
            <span style="color: #e2e8f0;"> — Dashboard consome API REST (como app mobile faria)</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════

with st.sidebar:
    st.markdown("## 🏗️ PICNEP")
    st.caption("Inteligência de Compras para PMEs")
    st.divider()

    if API_AVAILABLE and "client" in st.session_state:
        if st.button("🔄 Gerar Alertas", use_container_width=True):
            result = st.session_state.client.post("/api/v1/analysis/alerts/generate")
            if result:
                st.success(f"{result.get('total', 0)} alertas gerados!")

    st.divider()
    mode = "🟢 API" if API_AVAILABLE else "🟡 Demo"
    st.markdown(f"**Modo:** {mode}")
    st.markdown(f"**Usuário:** {st.session_state.user_name}")
    st.markdown(f"**Perfil:** {st.session_state.user_role}")

    st.divider()
    if st.button("🚪 Sair", use_container_width=True):
        st.session_state.logged_in = False
        if API_AVAILABLE:
            st.session_state.client = PicnepClient()
        st.rerun()

    st.divider()
    st.caption("Desenvolvido por Paulo Lavarini")


# ══════════════════════════════════════════
# ABAS
# ══════════════════════════════════════════

# Abas baseadas no perfil do usuário
tab5 = None

if st.session_state.user_role == "admin":
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Visão Geral",
        "💡 Recomendações",
        "🔔 Alertas",
        "📋 Dados",
        "👥 Admin",
    ])
else:
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Visão Geral",
        "💡 Recomendações",
        "🔔 Alertas",
        "📋 Dados",
    ])


# ══════════════════════════════════════════
# ABA 1: VISÃO GERAL
# ══════════════════════════════════════════

with tab1:
    suppliers = get_suppliers()
    items = get_items()
    quotes = get_quotes()
    purchases = get_purchases()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🏭 Fornecedores", len(suppliers))
    col2.metric("📦 Itens", len(items))
    col3.metric("📋 Cotações", len(quotes))
    col4.metric("🛒 Compras", len(purchases))

    st.divider()

    if quotes:
        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("Cotações por Fornecedor")
            supplier_counts = {}
            for q in quotes:
                sid = q.get("supplier_id", 0)
                s_name = f"Fornecedor {sid}"
                for s in suppliers:
                    if s.get("id") == sid:
                        s_name = s.get("name", s_name)
                        break
                supplier_counts[s_name] = supplier_counts.get(s_name, 0) + 1

            if supplier_counts:
                import plotly.express as px
                fig = px.pie(
                    names=list(supplier_counts.keys()),
                    values=list(supplier_counts.values()),
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Set2,
                )
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#e2e8f0"), height=350,
                )
                st.plotly_chart(fig, use_container_width=True)

        with col_right:
            st.subheader("Maiores Valores Cotados")
            item_totals = {}
            for q in quotes:
                iid = q.get("item_id", 0)
                i_name = f"Item {iid}"
                for it in items:
                    if it.get("id") == iid:
                        i_name = it.get("name", i_name)
                        break
                item_totals[i_name] = item_totals.get(i_name, 0) + q.get("total_cost", 0)

            if item_totals:
                sorted_items = sorted(item_totals.items(), key=lambda x: x[1], reverse=True)[:8]
                fig = go.Figure(go.Bar(
                    x=[v for _, v in sorted_items],
                    y=[n for n, _ in sorted_items],
                    orientation="h", marker_color="#2563eb",
                    text=[f"R$ {v:,.0f}" for _, v in sorted_items],
                    textposition="outside",
                ))
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#e2e8f0"), yaxis=dict(autorange="reversed"), height=350,
                )
                st.plotly_chart(fig, use_container_width=True)

        st.divider()
        opps = get_opportunities()
        if opps:
            total_economia = sum(o.get("economia_potencial", 0) for o in opps)
            if total_economia > 0:
                st.markdown(f"### 💰 Economia Potencial: **R$ {total_economia:,.2f}**")
                st.caption(f"{len(opps)} oportunidades. Veja na aba Recomendações.")
    else:
        st.info("📤 Cadastre cotações para ver os gráficos.")


# ══════════════════════════════════════════
# ABA 2: RECOMENDAÇÕES
# ══════════════════════════════════════════

with tab2:
    st.subheader("💡 Recomendações de Compra")
    st.caption("Baseadas no Custo Efetivo Total e histórico de compras.")

    recs_list = get_recommendations()

    if recs_list:
        acoes = {}
        for rec in recs_list:
            if "erro" not in rec:
                acao = rec.get("acao", "desconhecido")
                acoes[acao] = acoes.get(acao, 0) + 1

        if acoes:
            cols = st.columns(len(acoes))
            icons = {
                "comprar_agora": ("🟢", "Comprar Agora"),
                "renegociar": ("🟡", "Renegociar"),
                "esperar": ("🔴", "Esperar"),
                "pedir_cotacao": ("⚪", "Pedir Cotação"),
            }
            for i, (acao, count) in enumerate(acoes.items()):
                icon, label = icons.get(acao, ("⚪", acao))
                cols[i].metric(f"{icon} {label}", count)

        st.divider()

        for rec in recs_list:
            if "erro" in rec:
                continue
            acao = rec.get("acao", "")
            icon = {"comprar_agora": "🟢", "renegociar": "🟡",
                    "esperar": "🔴", "pedir_cotacao": "⚪"}.get(acao, "⚪")
            economia = rec.get("economia_potencial", 0)
            economia_text = f" | 💰 **R$ {economia:,.2f}**" if economia > 0 else ""

            st.markdown(
                f"**{icon} {rec.get('item_name', 'Item')}** — "
                f"`{acao.upper().replace('_', ' ')}`{economia_text}"
            )
            st.caption(rec.get("motivo", ""))
            if rec.get("fornecedor_ideal"):
                st.caption(f"Fornecedor ideal: **{rec['fornecedor_ideal']}**")
            st.divider()
    else:
        st.info("Sem recomendações. Cadastre cotações e compras.")

    st.divider()
    st.subheader("📊 Ranking por Custo Efetivo Total")
    items_data = get_items()
    if items_data:
        selected_item = st.selectbox(
            "Selecione um item:",
            options=[(i["id"], i["name"]) for i in items_data],
            format_func=lambda x: x[1],
        )
        if selected_item:
            ranking = get_cost_ranking(selected_item[0])
            if ranking:
                for i, r in enumerate(ranking):
                    medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"#{i+1}"
                    c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
                    c1.markdown(f"{medal} **{r['supplier_name']}**")
                    c2.markdown(f"CET: **R$ {r['custo_real']:,.2f}**")
                    c3.markdown(f"Frete: R$ {r['custo_frete']:.2f}")
                    c4.markdown(f"Prazo: {r['dias_pagamento']} dias")
            else:
                st.info("Sem cotações para este item.")


# ══════════════════════════════════════════
# ABA 3: ALERTAS
# ══════════════════════════════════════════

with tab3:
    st.subheader("🔔 Alertas Inteligentes")
    alerts_list = get_alerts()

    if alerts_list:
        severities = {}
        for a in alerts_list:
            sev = a.get("severity", "info")
            severities[sev] = severities.get(sev, 0) + 1

        c1, c2, c3 = st.columns(3)
        c1.metric("🟢 Info", severities.get("info", 0))
        c2.metric("🟡 Warning", severities.get("warning", 0))
        c3.metric("🔴 Critical", severities.get("critical", 0))
        st.divider()

        for a in alerts_list:
            sev_icon = {"info": "🟢", "warning": "🟡", "critical": "🔴"}.get(
                a.get("severity", ""), "⚪")
            st.markdown(
                f"{sev_icon} **{a.get('type', '').replace('_', ' ').upper()}** — "
                f"{a.get('message', '')}"
            )
            economia = 0
            if a.get("data") and isinstance(a["data"], dict):
                economia = a["data"].get("economia_potencial", 0)
            if economia > 0:
                st.caption(f"💰 Economia: R$ {economia:,.2f}")
            st.divider()

        st.caption(f"Total: {len(alerts_list)} alertas")
    else:
        st.info("Sem alertas. Clique em '🔄 Gerar Alertas' na sidebar.")


# ══════════════════════════════════════════
# ABA 4: DADOS
# ══════════════════════════════════════════

with tab4:
    st.subheader("📋 Dados Cadastrados")
    data_tab = st.selectbox("Visualizar:", ["Fornecedores", "Itens", "Cotações", "Compras"])

    lookup = {
        "Fornecedores": get_suppliers,
        "Itens": get_items,
        "Cotações": get_quotes,
        "Compras": get_purchases,
    }

    data = lookup[data_tab]()
    if data:
        st.dataframe(data, use_container_width=True, hide_index=True)
        st.caption(f"{len(data)} registros")
    else:
        st.info(f"Nenhum registro em {data_tab}.")

    st.divider()
    st.subheader("🔄 Arquitetura")
    st.code("""
  Dashboard (Streamlit) ──HTTP──> FastAPI ──> PostgreSQL
                                    ↕
                            Engine de Análise
                          (CET + Recomendação)
    """, language="text")

# ══════════════════════════════════════════
# ABA 5: ADMIN (só para admin)
# ══════════════════════════════════════════

if tab5 is not None:
    with tab5:
        st.subheader("👥 Gestão de Usuários")
        st.caption("Apenas administradores podem gerenciar usuários")

        # Listar usuários
        users = []
        if API_AVAILABLE and "client" in st.session_state:
            users = st.session_state.client.get("/api/v1/users") or []
        else:
            db = SessionLocal()
            try:
                users = [{"id": u.id, "name": u.name, "email": u.email,
                          "role": u.role, "is_active": u.is_active,
                          "created_at": str(u.created_at)}
                         for u in db.query(User).all()]
            finally:
                db.close()

        if users:
            # Tabela de usuários
            for u in users:
                col1, col2, col3, col4 = st.columns([3, 3, 2, 2])

                role_icon = {"admin": "🔴", "gestor": "🟡", "analista": "🟢"}.get(
                    u.get("role", ""), "⚪"
                )
                active_icon = "✅" if u.get("is_active", True) else "❌"

                col1.markdown(f"**{u.get('name', '')}**")
                col2.markdown(f"{u.get('email', '')}")
                col3.markdown(f"{role_icon} {u.get('role', '').capitalize()}")
                col4.markdown(f"{active_icon} {'Ativo' if u.get('is_active') else 'Inativo'}")

            st.caption(f"Total: {len(users)} usuários")
        else:
            st.info("Nenhum usuário cadastrado.")

        st.divider()

        # Criar novo usuário
        st.subheader("➕ Criar Novo Usuário")

        with st.form("create_user_form"):
            new_name = st.text_input("Nome")
            new_email = st.text_input("Email")
            new_password = st.text_input("Senha", type="password")
            new_role = st.selectbox("Perfil", ["analista", "gestor", "admin"])

            submitted = st.form_submit_button("Criar Usuário", type="primary")

            if submitted and new_name and new_email and new_password:
                if API_AVAILABLE and "client" in st.session_state:
                    result = st.session_state.client.post("/api/v1/users", json={
                        "name": new_name,
                        "email": new_email,
                        "password": new_password,
                        "role": new_role,
                    })
                    if result:
                        st.success(f"Usuário {new_name} criado como {new_role}!")
                        st.rerun()
                    else:
                        st.error("Erro ao criar. Email pode já existir.")
                else:
                    db = SessionLocal()
                    try:
                        existing = db.query(User).filter(User.email == new_email).first()
                        if existing:
                            st.error("Email já cadastrado.")
                        else:
                            user = User(
                                name=new_name,
                                email=new_email,
                                password_hash=hash_password(new_password),
                                role=new_role,
                            )
                            db.add(user)
                            db.commit()
                            st.success(f"Usuário {new_name} criado como {new_role}!")
                            st.rerun()
                    finally:
                        db.close()

        # Perfis explicados
        st.divider()
        st.subheader("📋 Perfis de Acesso")
        st.markdown("""
        | Perfil | O que pode fazer |
        |--------|-----------------|
        | 🔴 **Admin** | Tudo: gerenciar usuários, configurar sistema, CRUD completo, ver análises |
        | 🟡 **Gestor** | Dashboard, gerar relatórios, upload cotações, ver recomendações |
        | 🟢 **Analista** | Consultar dados, exportar CSV, ver alertas (sem editar) |
        """)