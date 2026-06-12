"""
Dashboard EMAE – SECOPI 2023-2025
Colombia Compra Eficiente | Subdirección EMAE
Página principal: KPIs ejecutivos + Resumen por escenario
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# ── Configuración de página ───────────────────────────────────────────────
st.set_page_config(
    page_title="EMAE Dashboard",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "Dashboard analítico EMAE | Colombia Compra Eficiente"},
)

sys.path.insert(0, str(Path(__file__).parent))
from utils.data_loader import load_data, apply_filters, fmt_billones, fmt_numero
from utils.charts import (
    chart_dona_escenarios,
    chart_barras_escenario_vigencia,
    chart_timeline,
    ESCENARIO_COLORS,
    ESCENARIO_LABELS,
    CCE_AZUL, CCE_VERDE,
)

# ── CSS Institucional ─────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #174073 0%, #3E546C 100%);
}
[data-testid="stSidebar"] * {
    color: #fff !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stRadio label {
    color: #D98A3C !important;
    font-size: 0.82rem;
    font-weight: 500;
    letter-spacing: 0.03em;
    text-transform: uppercase;
}

/* KPI Cards */
.kpi-card {
    background: white;
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    border-left: 5px solid #174073;
    box-shadow: 0 4px 20px rgba(23,64,115,0.10);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.kpi-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 30px rgba(23,64,115,0.18);
}
.kpi-card.verde  { border-left-color: #3E546C; }
.kpi-card.rojo   { border-left-color: #D61C38; }
.kpi-card.naranja{ border-left-color: #D98A3C; }

.kpi-label {
    font-size: 0.78rem;
    font-weight: 600;
    color: #5A666A;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 0.3rem;
}
.kpi-value {
    font-size: 2rem;
    font-weight: 700;
    color: #174073;
    line-height: 1.1;
}
.kpi-sub {
    font-size: 0.75rem;
    color: #5A666A;
    margin-top: 0.3rem;
}

/* Escenario badges */
.badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    color: white;
    margin: 0.15rem;
}

/* Sección headers */
.section-header {
    font-size: 1.15rem;
    font-weight: 700;
    color: #174073;
    border-bottom: 3px solid #D61C38;
    padding-bottom: 0.4rem;
    margin: 1.5rem 0 1rem 0;
}

/* Escenario cards en resumen */
.esc-card {
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    color: white;
    box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    transition: transform 0.2s;
}
.esc-card:hover { transform: translateY(-2px); }
.esc-card .esc-name { font-size: 0.78rem; font-weight:600; opacity:0.85; letter-spacing:0.04em; }
.esc-card .esc-val  { font-size: 1.7rem; font-weight:700; line-height:1.1; }
.esc-card .esc-sub  { font-size: 0.73rem; opacity:0.8; margin-top:0.25rem; }

/* Header principal */
.main-header {
    background: linear-gradient(135deg, #174073 0%, #533965 60%, #6A2444 100%);
    border-radius: 18px;
    padding: 2rem 2.5rem;
    color: white;
    margin-bottom: 1.5rem;
    box-shadow: 0 6px 30px rgba(23,64,115,0.25);
    position: relative;
    overflow: hidden;
}
.color-strip {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 8px;
    background: linear-gradient(to right, 
        #FFC000 0% 10%, 
        #D98A3C 10% 20%, 
        #9C7238 20% 30%, 
        #5A666A 30% 40%, 
        #3E546C 40% 50%, 
        #174073 50% 60%, 
        #533965 60% 70%, 
        #6A2444 70% 80%, 
        #9E2044 80% 90%, 
        #D61C38 90% 100%
    );
}
.main-header h1 {
    font-size: 1.7rem;
    font-weight: 700;
    margin: 0;
    line-height: 1.2;
    padding-top: 0.5rem;
}
.main-header p {
    font-size: 0.9rem;
    opacity: 0.85;
    margin: 0.5rem 0 0 0;
}
.main-header .tag {
    background: rgba(255,255,255,0.2);
    border-radius: 20px;
    padding: 0.2rem 0.8rem;
    font-size: 0.75rem;
    font-weight: 600;
    display: inline-block;
    margin-top: 0.6rem;
    margin-right: 0.4rem;
}
</style>
""", unsafe_allow_html=True)

# ── Carga de datos ────────────────────────────────────────────────────────
df_raw = load_data()

# ── SIDEBAR ───────────────────────────────────────────────────────────────
with st.sidebar:
    import os
    logo_path = Path(__file__).parent / "assets" / "escudo.png"
    if logo_path.exists():
        st.image(str(logo_path), use_container_width=True)
    else:
        st.markdown("*(Coloca la imagen en assets/escudo.png para visualizarla)*")
    
    st.markdown("## 🏛️ EMAE – SECOPI")
    st.markdown("**Colombia Compra Eficiente**")
    st.markdown("---")

    vigencias_disp = sorted(df_raw["VIGENCIA"].dropna().unique().tolist())
    sel_vigencia = st.multiselect(
        "Vigencia",
        options=["Todas"] + vigencias_disp,
        default=["Todas"],
    )

    col_depto = "DEPARTAMENTO_MINTIC" if "DEPARTAMENTO_MINTIC" in df_raw.columns else "DEPARTAMENTO_SECOPI"
    deptos_disp = sorted(df_raw[col_depto].dropna().unique().tolist())
    sel_depto = st.multiselect("Departamento", options=deptos_disp, default=[])

    escenarios_disp = [k for k in ESCENARIO_LABELS if k in df_raw["ESCENARIO_REPORTE_FINAL"].unique()]
    sel_escenario = st.multiselect(
        "Escenario de reporte",
        options=escenarios_disp,
        format_func=lambda x: ESCENARIO_LABELS.get(x, x),
        default=[],
    )

    regimenes_disp = sorted(df_raw["REGIMEN_CLASIFICADO_FINAL"].dropna().unique().tolist())
    sel_regimen = st.multiselect("Régimen", options=regimenes_disp, default=[])

    st.markdown("---")
    st.caption(f"📊 Base: {len(df_raw):,} registros totales")
    st.caption("Subdirección EMAE | Jun 2026")

# ── Filtro aplicado ───────────────────────────────────────────────────────
df = apply_filters(df_raw, sel_vigencia, sel_depto, sel_escenario, sel_regimen)

# ── HEADER PRINCIPAL ──────────────────────────────────────────────────────
st.markdown(f"""
<div class="main-header">
    <div class="color-strip"></div>
    <h1>🏛️ Dashboard EMAE – SECOPI 2023–2025</h1>
    <p>Análisis descriptivo de contratación registrada en SECOP I y validación del universo de entidades obligadas a publicar en SECOP II</p>
    <span class="tag">📅 Vigencias 2023–2025</span>
    <span class="tag">🏢 Colombia Compra Eficiente</span>
    <span class="tag">📋 {len(df):,} registros seleccionados</span>
</div>
""", unsafe_allow_html=True)

# ── KPIs PRINCIPALES ──────────────────────────────────────────────────────
st.markdown('<div class="section-header">📦 Indicadores Clave</div>', unsafe_allow_html=True)

total_contratos = len(df)
total_entidades = df["NOMBRE_ENTIDAD_SECOPI"].nunique()
valor_total = df["VALOR_CONTRATO_CON_ADICIONES"].sum()
obligadas_ids = df[df.get("ENTIDAD_EN_CIRCULAR_674_FINAL", pd.Series(dtype=str)) == "SI"]["NOMBRE_ENTIDAD_SECOPI"].nunique() if "ENTIDAD_EN_CIRCULAR_674_FINAL" in df.columns else 0

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Total Contratos</div>
        <div class="kpi-value">{fmt_numero(total_contratos)}</div>
        <div class="kpi-sub">registros en SECOP I</div>
    </div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""
    <div class="kpi-card verde">
        <div class="kpi-label">Entidades Identificadas</div>
        <div class="kpi-value">{fmt_numero(total_entidades)}</div>
        <div class="kpi-sub">que publican en SECOP I</div>
    </div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""
    <div class="kpi-card naranja">
        <div class="kpi-label">Valor Total Contratado</div>
        <div class="kpi-value">{fmt_billones(valor_total)}</div>
        <div class="kpi-sub">suma de contratos</div>
    </div>""", unsafe_allow_html=True)
with k4:
    st.markdown(f"""
    <div class="kpi-card rojo">
        <div class="kpi-label">Entidades Obligadas Detectadas</div>
        <div class="kpi-value">{fmt_numero(obligadas_ids) if obligadas_ids else "—"}</div>
        <div class="kpi-sub">del universo de 674</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── ESCENARIOS ────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">🔑 Distribución por Escenario Analítico</div>', unsafe_allow_html=True)

esc_counts = df["ESCENARIO_REPORTE_FINAL"].value_counts()
esc_valor  = df.groupby("ESCENARIO_REPORTE_FINAL", observed=True)["VALOR_CONTRATO_CON_ADICIONES"].sum()

ec1, ec2, ec3, ec4 = st.columns(4)
esc_cols = [ec1, ec2, ec3, ec4]
esc_order = [
    "OBLIGADA_CIRCULAR_Y_LEY80",
    "OBLIGADA_CIRCULAR_PERO_NO_LEY80",
    "NO_CIRCULAR_PERO_LEY80",
    "NO_CIRCULAR_NO_LEY80",
]
for col_ui, esc_key in zip(esc_cols, esc_order):
    cnt = esc_counts.get(esc_key, 0)
    val = esc_valor.get(esc_key, 0)
    color = ESCENARIO_COLORS.get(esc_key, "#6C757D")
    label = ESCENARIO_LABELS.get(esc_key, esc_key)
    pct = cnt / total_contratos * 100 if total_contratos > 0 else 0
    with col_ui:
        st.markdown(f"""
        <div class="esc-card" style="background:{color};">
            <div class="esc-name">{label}</div>
            <div class="esc-val">{cnt:,}</div>
            <div class="esc-sub">{pct:.1f}% de contratos</div>
            <div class="esc-sub">{fmt_billones(val)}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── GRÁFICOS PRINCIPALES ─────────────────────────────────────────────────
st.markdown('<div class="section-header">📊 Análisis Visual</div>', unsafe_allow_html=True)

g1, g2 = st.columns([1, 1.8])
with g1:
    st.markdown("**Distribución por escenario**")
    st.plotly_chart(chart_dona_escenarios(df), use_container_width=True, key="dona_esc")

with g2:
    metrica = st.radio(
        "Ver por:",
        ["contratos", "valor"],
        format_func=lambda x: "N° de Contratos" if x == "contratos" else "Valor Contratado",
        horizontal=True,
        key="metrica_radio",
    )
    st.markdown("**Escenarios por vigencia**")
    st.plotly_chart(
        chart_barras_escenario_vigencia(df, metrica),
        use_container_width=True,
        key="barras_vig",
    )

# ── TIMELINE ──────────────────────────────────────────────────────────────
if "FECHA_FIRMA_CONTRATO" in df.columns and df["FECHA_FIRMA_CONTRATO"].notna().sum() > 0:
    st.markdown('<div class="section-header">📅 Evolución Temporal de Contratos</div>', unsafe_allow_html=True)
    st.plotly_chart(chart_timeline(df), use_container_width=True, key="timeline")

# ── TABLA RESUMEN RÁPIDO ───────────────────────────────────────────────────
with st.expander("📋 Ver resumen estadístico por vigencia", expanded=False):
    resumen = (df.groupby("VIGENCIA", observed=True)
                 .agg(
                     Contratos=("UID", "count"),
                     Entidades=("NOMBRE_ENTIDAD_SECOPI", "nunique"),
                     Valor_Total=("VALOR_CONTRATO_CON_ADICIONES", "sum"),
                 )
                 .reset_index()
                 .rename(columns={"VIGENCIA": "Vigencia", "Valor_Total": "Valor Contratado (COP)"}))
    resumen["Valor Contratado (COP)"] = resumen["Valor Contratado (COP)"].apply(fmt_billones)
    resumen["Contratos"] = resumen["Contratos"].apply(lambda x: f"{x:,}")
    resumen["Entidades"] = resumen["Entidades"].apply(lambda x: f"{x:,}")
    st.dataframe(resumen, use_container_width=True, hide_index=True)
