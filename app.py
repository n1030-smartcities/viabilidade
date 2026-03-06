import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

from src.engine.project import calculate_project
from src.engine.land_residual import calculate_residual_land_value
from src.types.project_types import (
    ProjectInput,
    PhysicalInput,
    LandInput,
    OperationalInput,
    SalesInput,
    PaymentPlanInput,
    MensaisInput,
)

st.set_page_config(
    page_title="Viabilidade Imobiliaria",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e0e0e0; }
        .block-container { padding-top: 1.5rem; }
        div[data-testid="metric-container"] {
            background-color: #ffffff;
            border: 1px solid #e8ecf0;
            border-radius: 10px;
            padding: 16px 20px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.06);
        }
        div[data-testid="metric-container"] label { font-size: 0.78rem; color: #6b7280; }
        div[data-testid="metric-container"] [data-testid="stMetricValue"] { font-size: 1.5rem; font-weight: 700; color: #1a1a2e; }
        .section-divider { border-top: 1px solid #e8ecf0; margin: 1rem 0; }
        .stButton > button[kind="primary"] { background-color: #1a56db; border: none; font-weight: 600; }
        .stButton > button[kind="primary"]:hover { background-color: #1447c0; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Parametros do Projeto")

    st.markdown("### Dados Fisicos")
    land_area = st.number_input("Area do Terreno (m²)", min_value=100.0, value=5000.0, step=100.0, format="%.0f")
    ca = st.number_input("CA (Coef. de Aproveitamento)", min_value=0.1, max_value=10.0, value=2.0, step=0.1)
    efficiency_rate = st.slider("Eficiencia (%)", min_value=50, max_value=95, value=85, step=1)
    area_per_unit = st.number_input("Area por Unidade (m²)", min_value=20.0, value=70.0, step=5.0)
    ticket_medio = st.number_input("Ticket Medio (R$)", min_value=50_000, value=500_000, step=10_000, format="%d")

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("### Terreno")

    acquisition_type = st.selectbox(
        "Tipo de Aquisicao",
        ["DINHEIRO", "PERMUTA_FINANCEIRA", "PERMUTA_FISICA"],
        format_func=lambda x: {
            "DINHEIRO": "Dinheiro",
            "PERMUTA_FINANCEIRA": "Permuta Financeira",
            "PERMUTA_FISICA": "Permuta Fisica",
        }[x],
    )
    land_value = None
    permuta_percent = None
    if acquisition_type == "DINHEIRO":
        land_value = st.number_input("Valor do Terreno (R$)", min_value=0, value=5_000_000, step=100_000, format="%d")
    else:
        permuta_percent = st.slider("Percentual de Permuta (%)", min_value=1, max_value=50, value=15) / 100

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("### Operacional")

    cost_per_m2 = st.number_input("Custo por m² de Obra (R$)", min_value=500, value=2500, step=100, format="%d")
    prazo_total = int(st.number_input("Prazo Total (meses)", min_value=12, max_value=120, value=48, step=6))
    prazo_obra = int(st.number_input("Prazo de Obra (meses)", min_value=6, max_value=prazo_total, value=min(36, prazo_total), step=6))
    prazo_vendas = int(st.number_input("Prazo de Vendas (meses)", min_value=6, max_value=prazo_total, value=min(24, prazo_total), step=6))
    tma_pct = st.slider("TMA (% ao mes)", min_value=0.5, max_value=3.0, value=1.2, step=0.1)
    tma = tma_pct / 100

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("### Plano de Pagamento")

    entrada_pct = st.slider("Entrada (%)", min_value=5, max_value=60, value=20, step=5)
    chaves_pct = st.slider("Chaves (%)", min_value=5, max_value=60, value=30, step=5)
    mensais_pct = 100 - entrada_pct - chaves_pct

    if mensais_pct <= 0:
        st.error("Entrada + Chaves nao pode ser >= 100%. Ajuste os valores.")
        valid_payment = False
    else:
        st.info(f"Mensais: **{mensais_pct}%**")
        valid_payment = True

    prazo_mensais = int(st.number_input("Prazo das Mensais (meses)", min_value=6, max_value=60, value=24, step=6))

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    calc_button = st.button("Calcular Viabilidade", use_container_width=True, type="primary")

# ── Session state ──────────────────────────────────────────────────────────────
if "result" not in st.session_state:
    st.session_state.result = None
    st.session_state.project = None

# ── Calculate ──────────────────────────────────────────────────────────────────
if calc_button and valid_payment:
    project = ProjectInput(
        physical=PhysicalInput(
            land_area=land_area,
            ca=ca,
            efficiency_rate=efficiency_rate / 100,
            area_per_unit=area_per_unit,
            ticket_medio=float(ticket_medio),
        ),
        land=LandInput(
            acquisition_type=acquisition_type,
            land_value=float(land_value) if land_value is not None else None,
            permuta_percent=permuta_percent,
        ),
        operational=OperationalInput(
            cost_per_m2=float(cost_per_m2),
            prazo_total=prazo_total,
            prazo_obra=prazo_obra,
            prazo_vendas=prazo_vendas,
            tma=tma,
        ),
        sales=SalesInput(mode="PROFILE", profile="BASE"),
        payment_plan=PaymentPlanInput(
            entrada=entrada_pct / 100,
            chaves=chaves_pct / 100,
            mensais=MensaisInput(percentual=mensais_pct / 100, meses=prazo_mensais),
        ),
    )
    with st.spinner("Calculando..."):
        st.session_state.result = calculate_project(project)
        st.session_state.project = project

# ── Main area ──────────────────────────────────────────────────────────────────
st.markdown("## Analise de Viabilidade Imobiliaria")

if st.session_state.result is None:
    st.markdown(
        """
        <div style="background:#ffffff;border:1px solid #e8ecf0;border-radius:12px;padding:40px;text-align:center;margin-top:40px;">
            <h3 style="color:#6b7280;font-weight:400;">Configure os parametros no painel lateral e clique em <b>Calcular Viabilidade</b></h3>
            <p style="color:#9ca3af;font-size:0.9rem;">Os resultados incluem TIR, VPL, fluxo de caixa mensal e calculo do valor residual do terreno.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    result = st.session_state.result
    project = st.session_state.project
    core = result["core"]
    cashflow = result["cashflow"]
    metrics = result["metrics"]

    irr_monthly = metrics["irr"]
    irr_annual = (1 + irr_monthly) ** 12 - 1
    npv = metrics["npv"]
    resultado_bruto = core.vgv - core.cost_total - core.land_value
    margem = resultado_bruto / core.vgv * 100 if core.vgv > 0 else 0

    # ── KPI cards ──────────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Unidades", f"{core.units}")
    c2.metric("VGV", f"R$ {core.vgv / 1e6:.2f}M")
    c3.metric("Custo de Obra", f"R$ {core.cost_total / 1e6:.2f}M")
    c4.metric("TIR (a.a.)", f"{irr_annual * 100:.1f}%")
    c5.metric("VPL", f"R$ {npv / 1e6:.2f}M")
    c6.metric("Margem Bruta", f"{margem:.1f}%")

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ── Cashflow chart ─────────────────────────────────────────────────────────
    st.markdown("### Fluxo de Caixa Mensal")

    months = [m.month for m in cashflow]
    inflows = [m.inflow / 1e6 for m in cashflow]
    outflows = [-m.outflow / 1e6 for m in cashflow]
    accumulated = [m.accumulated / 1e6 for m in cashflow]

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(
            name="Receitas",
            x=months,
            y=inflows,
            marker_color="#22c55e",
            marker_line_width=0,
            opacity=0.85,
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Bar(
            name="Custos",
            x=months,
            y=outflows,
            marker_color="#ef4444",
            marker_line_width=0,
            opacity=0.85,
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            name="Acumulado",
            x=months,
            y=accumulated,
            line=dict(color="#1a56db", width=2.5),
            mode="lines",
        ),
        secondary_y=True,
    )

    fig.update_layout(
        barmode="relative",
        paper_bgcolor="#ffffff",
        plot_bgcolor="#f8f9fa",
        font=dict(family="Inter, sans-serif", size=12, color="#374151"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(255,255,255,0)",
        ),
        xaxis=dict(
            title="Mes",
            gridcolor="#e5e7eb",
            showgrid=True,
            zeroline=False,
        ),
        margin=dict(l=0, r=0, t=30, b=0),
        height=380,
    )
    fig.update_yaxes(
        title_text="R$ Milhoes (fluxo)",
        gridcolor="#e5e7eb",
        zeroline=True,
        zerolinecolor="#9ca3af",
        secondary_y=False,
    )
    fig.update_yaxes(
        title_text="R$ Milhoes (acumulado)",
        gridcolor=None,
        showgrid=False,
        secondary_y=True,
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ── Summary + Land residual ────────────────────────────────────────────────
    col_left, col_gap, col_right = st.columns([5, 1, 4])

    with col_left:
        st.markdown("### Resumo do Empreendimento")
        summary = {
            "Indicador": [
                "Area do Terreno",
                "Area Construivel",
                "Unidades",
                "VGV Total",
                "Custo de Obra",
                "Valor do Terreno",
                "Resultado Bruto",
                "Margem Bruta",
                "TIR (a.m.)",
                "TIR (a.a.)",
                "VPL",
            ],
            "Valor": [
                f"{project.physical.land_area:,.0f} m²",
                f"{core.buildable_area:,.0f} m²",
                f"{core.units} unidades",
                f"R$ {core.vgv:,.0f}",
                f"R$ {core.cost_total:,.0f}",
                f"R$ {core.land_value:,.0f}",
                f"R$ {resultado_bruto:,.0f}",
                f"{margem:.1f}%",
                f"{irr_monthly * 100:.2f}%",
                f"{irr_annual * 100:.1f}%",
                f"R$ {npv:,.0f}",
            ],
        }
        st.dataframe(
            pd.DataFrame(summary),
            use_container_width=True,
            hide_index=True,
            height=423,
        )

    with col_right:
        st.markdown("### Valor Residual do Terreno")
        st.markdown(
            "<p style='color:#6b7280;font-size:0.88rem;'>Calcula o valor maximo que pode ser pago pelo terreno para atingir uma TIR alvo.</p>",
            unsafe_allow_html=True,
        )

        target_irr_annual_pct = st.slider(
            "TIR Alvo (% a.a.)", min_value=10, max_value=50, value=20, step=1, key="residual_irr"
        )
        target_irr_annual = target_irr_annual_pct / 100
        target_irr_monthly = (1 + target_irr_annual) ** (1 / 12) - 1

        if st.button("Calcular Valor Residual", use_container_width=True):
            with st.spinner("Calculando..."):
                residual = calculate_residual_land_value(
                    project, target_irr=target_irr_monthly
                )
            if residual:
                res_irr_annual = (1 + residual["irr"]) ** 12 - 1
                st.markdown(
                    f"""
                    <div style="background:#f0f9ff;border:1px solid #bae6fd;border-radius:10px;padding:20px;margin-top:12px;">
                        <p style="color:#0369a1;font-size:0.85rem;margin:0 0 4px 0;">VALOR MAXIMO DO TERRENO</p>
                        <p style="font-size:1.8rem;font-weight:700;color:#0c4a6e;margin:0;">R$ {residual["land_value"]:,.0f}</p>
                        <hr style="border:none;border-top:1px solid #bae6fd;margin:12px 0;">
                        <p style="color:#374151;font-size:0.88rem;margin:0;">TIR resultante: <b>{res_irr_annual * 100:.1f}% a.a.</b></p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.warning("Nao foi possivel calcular o valor residual.")

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ── Detailed table ─────────────────────────────────────────────────────────
    with st.expander("Tabela de Fluxo de Caixa Detalhado"):
        cf_df = pd.DataFrame(
            [
                {
                    "Mes": m.month,
                    "Receitas (R$)": f"{m.inflow:,.0f}",
                    "Custos (R$)": f"{m.outflow:,.0f}",
                    "Liquido (R$)": f"{m.net:,.0f}",
                    "Acumulado (R$)": f"{m.accumulated:,.0f}",
                }
                for m in cashflow
            ]
        )
        st.dataframe(cf_df, use_container_width=True, hide_index=True, height=350)
