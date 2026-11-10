"""
Página: Análisis por Entidades – Ficha de Homologación SECOP I / SECOP II, Rankings y Directorio
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.data_loader import (
    load_data,
    render_sidebar_filters,
    fmt_billones,
    fmt_numero,
    ESCENARIO_LABELS,
    ESCENARIO_COLORS,
)
from utils.charts import (
    chart_top_entidades,
    chart_modalidad,
    CCE_AZUL,
    CCE_NARANJA,
    CCE_ROJO,
    LAYOUT_DEFAULTS,
)

st.set_page_config(page_title="Entidades | EMAE Dashboard", page_icon="🏢", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html,[class*="css"]{font-family:'Inter',sans-serif;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#174073 0%,#3E546C 100%);}
[data-testid="stSidebar"] *{color:#fff!important;}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stRadio label{color:#FFC000!important;font-size:0.80rem;font-weight:600;text-transform:uppercase;letter-spacing:0.03em;}
.section-header{font-size:1.15rem;font-weight:700;color:#174073;border-bottom:3px solid #D61C38;padding-bottom:0.4rem;margin:1.5rem 0 1rem 0;}
.entity-card{background:white;border-radius:14px;padding:1.3rem 1.6rem;box-shadow:0 4px 18px rgba(23,64,115,0.10);border-top:5px solid #174073;margin-bottom:0.8rem;}
.entity-card h3{color:#174073;font-size:1.1rem;margin:0 0 0.55rem 0;}
.entity-row{display:flex;gap:0.75rem;flex-wrap:wrap;margin-top:0.55rem;}
.entity-stat{background:#F0F6FF;border-radius:8px;padding:0.4rem 0.8rem;font-size:0.8rem;color:#174073;font-weight:600;}
.badge{display:inline-block;padding:.22rem .75rem;border-radius:999px;font-size:.73rem;font-weight:600;color:white;margin:.12rem;}
</style>
""", unsafe_allow_html=True)

df_raw = load_data()
df = render_sidebar_filters(df_raw)

total_proc = int(df["CANTIDAD_PROCESOS"].sum())
total_ent = int(df["NOMBRE_ENTIDAD"].nunique())
total_nits = int(df.loc[df["NIT_HOMOLOGADO"] != "Sin NIT Válido", "NIT_HOMOLOGADO"].nunique())

st.markdown("# 🏢 Análisis por Entidades y Homologación SECOP II")
st.markdown(
    f"Mostrando **{total_proc:,}** procesos de **{total_ent:,}** cuentas de entidades compradoras "
    f"(**{total_nits:,}** NITs únicos homologados)"
)

# ── BUSCADOR DE ENTIDAD ────────────────────────────────────────────────────
st.markdown('<div class="section-header">🔍 Ficha Técnica y Homologación de Entidad (SECOP I ↔ SECOP II)</div>', unsafe_allow_html=True)

entidades_lista = sorted(df["NOMBRE_ENTIDAD"].dropna().unique().tolist())
entidad_sel = st.selectbox("Buscar entidad compradora en SECOP I:", ["— Seleccione una entidad —"] + entidades_lista)

if entidad_sel != "— Seleccione una entidad —":
    ent_df = df[df["NOMBRE_ENTIDAD"] == entidad_sel]
    row0 = ent_df.iloc[0]

    esc = row0["ESCENARIO_2026"]
    color_esc = ESCENARIO_COLORS.get(esc, "#6C757D")
    label_esc = ESCENARIO_LABELS.get(esc, esc)

    nat_inst = row0.get("NATURALEZA_INSTITUCIONAL", "N/D")
    tipo_ent = row0.get("TIPO_ENTIDAD", "N/D")
    nit_s1 = row0.get("NIT_ENTIDAD", "N/D")
    nit_hom = row0.get("NIT_HOMOLOGADO", "N/D")
    cuenta_s2 = row0.get("NOMBRE_ENTIDAD_SECOP2", "N/D")
    pub_s2 = row0.get("TIENE_PUBLICACIONES_SECOP2", "No")
    proc_hist_s2 = int(ent_df["PROCESOS_HISTORICOS_SECOP2"].max()) if "PROCESOS_HISTORICOS_SECOP2" in ent_df.columns else 0

    depto = row0.get("DEPARTAMENTO", "N/D")
    mpio = row0.get("MUNICIPIO", "N/D")
    divipola = row0.get("CODIGO_DIVIPOLA", "N/D")
    cat_cgn = row0.get("CATEGORIA_CGN", "N/D")
    pen_mintic = float(row0.get("PENETRACION_INTERNET_MINTIC", 0.0) or 0.0) * 100.0
    rango_mintic = row0.get("RANGO_CONECTIVIDAD_MINTIC", "N/D")
    detalle_obl = row0.get("DETALLE_OBLIGACION_PREVIA", "N/D")
    ruta_2026 = row0.get("CLASIFICACION_Y_RUTA_DESPLIEGUE_2026", "N/D")

    total_c = int(ent_df["CANTIDAD_PROCESOS"].sum())
    total_v = float(ent_df["VALOR_REAL_CUANTIA"].sum())

    f1, f2 = st.columns([1.85, 1.15])
    with f1:
        st.markdown(f"""
        <div class="entity-card">
            <h3>🏛️ {entidad_sel}</h3>
            <span class="badge" style="background:{color_esc};">{label_esc}</span>
            <span class="badge" style="background:#174073;">{nat_inst}</span>
            <span class="badge" style="background:#533965;">Categoría CGN: {cat_cgn}</span>
            <div class="entity-row">
                <div class="entity-stat">📋 NIT SECOP I: {nit_s1}</div>
                <div class="entity-stat">✅ NIT Homologado: {nit_hom}</div>
                <div class="entity-stat">🗺️ {depto} / {mpio} (DIVIPOLA: {divipola})</div>
                <div class="entity-stat">📄 {total_c:,} procesos en SECOP I</div>
                <div class="entity-stat">💰 {fmt_billones(total_v, short=True)}</div>
                <div class="entity-stat">📡 Internet MinTIC: {pen_mintic:.1f}% ({rango_mintic})</div>
            </div>
            <div class="entity-row" style="margin-top:0.65rem;">
                <div class="entity-stat" style="background:#EAFAF1;color:#1E8449;">🔗 Cuenta Oficial SECOP II: <b>{cuenta_s2}</b></div>
                <div class="entity-stat" style="background:#FEF9E7;color:#9C7238;">📊 Publica en SECOP II: <b>{pub_s2}</b> ({proc_hist_s2:,} proc. históricos)</div>
            </div>
            <div style="margin-top:0.65rem;font-size:0.80rem;color:#3E546C;">
                <b>⚖️ Trazabilidad Obligación:</b> {detalle_obl}<br>
                <b>🚀 Ruta Operativa 2026:</b> {ruta_2026}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with f2:
        vig_ent = (
            ent_df.groupby("VIGENCIA", observed=True)["CANTIDAD_PROCESOS"]
            .sum()
            .reset_index(name="procesos")
        )
        if not vig_ent.empty:
            fig_vig = px.bar(
                vig_ent,
                x="VIGENCIA",
                y="procesos",
                text="procesos",
                color_discrete_sequence=[CCE_AZUL],
                labels={"procesos": "Procesos SECOP I", "VIGENCIA": "Vigencia"},
                title="Evolución de Procesos en SECOP I (2023–2025)",
            )
            fig_vig.update_traces(texttemplate="%{text:,}", textposition="outside")
            fig_vig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=35, b=10),
                height=250,
                font=dict(family="Inter, Arial"),
            )
            st.plotly_chart(fig_vig, use_container_width=True, key="vig_ent")

# ── TOPS ──────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">🏆 Rankings de Entidades Compradoras</div>', unsafe_allow_html=True)

n_top = st.slider("Número de entidades a mostrar en el ranking:", 5, 30, 15, key="n_top")
t1, t2 = st.columns(2)

with t1:
    st.markdown("**Por número de procesos registrados en SECOP I**")
    st.plotly_chart(chart_top_entidades(df, n_top, "procesos"), use_container_width=True, key="top_c")

with t2:
    st.markdown("**Por cuantía real contratada (Billones COP)**")
    st.plotly_chart(chart_top_entidades(df, n_top, "valor"), use_container_width=True, key="top_v")

# ── MODALIDAD ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📑 Modalidades de Contratación</div>', unsafe_allow_html=True)

m1, m2 = st.columns(2)
with m1:
    st.markdown("**Proporción de procesos por modalidad agrupada**")
    st.plotly_chart(chart_modalidad(df, "pie"), use_container_width=True, key="mod_pie")

with m2:
    st.markdown("**Volumen de procesos por modalidad**")
    st.plotly_chart(chart_modalidad(df, "bar"), use_container_width=True, key="mod_bar")

# ── TABLA DESCARGABLE ─────────────────────────────────────────────────────
st.markdown('<div class="section-header">📋 Directorio Consolidado de Entidades (SECOP I vs. SECOP II)</div>', unsafe_allow_html=True)

cols_dir = [
    "NOMBRE_ENTIDAD",
    "NIT_ENTIDAD",
    "NIT_HOMOLOGADO",
    "NATURALEZA_INSTITUCIONAL",
    "DEPARTAMENTO",
    "MUNICIPIO",
    "CODIGO_DIVIPOLA",
    "CATEGORIA_CGN",
    "SEGMENTO_NORMATIVO",
    "ESTADO_OBLIGATORIEDAD",
    "NOMBRE_ENTIDAD_SECOP2",
    "TIENE_PUBLICACIONES_SECOP2",
]
cols_dir = [c for c in cols_dir if c in df.columns]

directorio = (
    df.groupby(cols_dir, observed=True, dropna=False)
    .agg(
        Procesos_S1=("CANTIDAD_PROCESOS", "sum"),
        Valor_Real=("VALOR_REAL_CUANTIA", "sum"),
        Procesos_Hist_S2=("PROCESOS_HISTORICOS_SECOP2", "max"),
    )
    .reset_index()
    .sort_values("Procesos_S1", ascending=False)
)

col_search, col_dl = st.columns([3, 1])
with col_search:
    filtro_txt = st.text_input("🔎 Filtrar directorio por nombre de entidad, municipio, NIT o cuenta SECOP II:", "")
with col_dl:
    st.write("")
    csv = directorio.to_csv(index=False).encode("utf-8-sig")
    st.download_button("⬇️ Descargar CSV", csv, "directorio_entidades_2026.csv", "text/csv")

if filtro_txt:
    mask = directorio["NOMBRE_ENTIDAD"].astype(str).str.contains(filtro_txt, case=False, na=False)
    for col_s in ["NIT_ENTIDAD", "NIT_HOMOLOGADO", "NOMBRE_ENTIDAD_SECOP2", "MUNICIPIO", "DEPARTAMENTO"]:
        if col_s in directorio.columns:
            mask |= directorio[col_s].astype(str).str.contains(filtro_txt, case=False, na=False)
    directorio = directorio[mask]

st.dataframe(
    directorio,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Valor_Real": st.column_config.NumberColumn("Cuantía Real (COP)", format="dollar"),
        "Procesos_S1": st.column_config.NumberColumn("Procesos SECOP I", format="%d"),
        "Procesos_Hist_S2": st.column_config.NumberColumn("Procesos Hist. SECOP II", format="%d"),
        "TIENE_PUBLICACIONES_SECOP2": st.column_config.TextColumn("¿Publica S2?"),
    },
    height=440,
)
