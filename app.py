"""
Dashboard EMAE – Estrategia de Despliegue SECOP II (2026) | Vigencias 2023-2025
Colombia Compra Eficiente | Subdirección EMAE & Subdirección IDT
Página principal: KPIs ejecutivos, Segmentos Normativos, Naturaleza Institucional y Mapa de Calor
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# ── Configuración de página ───────────────────────────────────────────────
st.set_page_config(
    page_title="EMAE Dashboard – Despliegue SECOP II 2026",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "Dashboard analítico EMAE – Base Maestra Despliegue SECOP II 2026 | Colombia Compra Eficiente"},
)

sys.path.insert(0, str(Path(__file__).parent))
from utils.data_loader import (
    load_data,
    load_geojson_departamentos,
    load_geojson_municipios,
    render_sidebar_filters,
    fmt_billones,
    fmt_numero,
    ESCENARIO_LABELS,
    ESCENARIO_COLORS,
)
from utils.charts import (
    chart_dona_escenarios,
    chart_barras_escenario_vigencia,
    chart_naturaleza_institucional,
    chart_mapa_calor_departamentos,
    chart_mapa_calor_municipios,
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
    color: #FFC000 !important;
    font-size: 0.80rem;
    font-weight: 600;
    letter-spacing: 0.03em;
    text-transform: uppercase;
}

/* KPI Cards */
.kpi-card {
    background: white;
    border-radius: 16px;
    padding: 1.25rem 1.4rem;
    border-left: 5px solid #174073;
    box-shadow: 0 4px 20px rgba(23,64,115,0.10);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    height: 100%;
}
.kpi-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 30px rgba(23,64,115,0.18);
}
.kpi-card.verde   { border-left-color: #3E546C; }
.kpi-card.rojo    { border-left-color: #D61C38; }
.kpi-card.naranja { border-left-color: #D98A3C; }
.kpi-card.morado  { border-left-color: #533965; }

.kpi-label {
    font-size: 0.74rem;
    font-weight: 700;
    color: #5A666A;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.25rem;
}
.kpi-value {
    font-size: 1.75rem;
    font-weight: 700;
    color: #174073;
    line-height: 1.15;
}
.kpi-sub {
    font-size: 0.75rem;
    color: #5A666A;
    margin-top: 0.3rem;
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
    padding: 1.15rem 1.35rem;
    color: white;
    box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    transition: transform 0.2s;
    height: 100%;
}
.esc-card:hover { transform: translateY(-2px); }
.esc-card .esc-name { font-size: 0.78rem; font-weight:600; opacity:0.92; letter-spacing:0.03em; min-height: 2.2rem; }
.esc-card .esc-val  { font-size: 1.65rem; font-weight:700; line-height:1.15; margin-top: 0.2rem; }
.esc-card .esc-sub  { font-size: 0.75rem; opacity:0.88; margin-top:0.25rem; }

/* Header principal */
.main-header {
    background: linear-gradient(135deg, #174073 0%, #533965 60%, #6A2444 100%);
    border-radius: 18px;
    padding: 1.8rem 2.3rem;
    color: white;
    margin-bottom: 1.4rem;
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
    font-size: 1.65rem;
    font-weight: 700;
    margin: 0;
    line-height: 1.2;
    padding-top: 0.4rem;
}
.main-header p {
    font-size: 0.9rem;
    opacity: 0.9;
    margin: 0.45rem 0 0 0;
}
.main-header .tag {
    background: rgba(255,255,255,0.2);
    border-radius: 20px;
    padding: 0.22rem 0.85rem;
    font-size: 0.75rem;
    font-weight: 600;
    display: inline-block;
    margin-top: 0.65rem;
    margin-right: 0.4rem;
}
</style>
""", unsafe_allow_html=True)

# ── Carga de datos y Sidebar ──────────────────────────────────────────────
df_raw = load_data()
df = render_sidebar_filters(df_raw)

total_procesos = int(df["CANTIDAD_PROCESOS"].sum())
total_entidades = int(df["NOMBRE_ENTIDAD"].nunique())
total_nits = int(df.loc[df["NIT_HOMOLOGADO"] != "Sin NIT Válido", "NIT_HOMOLOGADO"].nunique())
valor_real_total = float(df["VALOR_REAL_CUANTIA"].sum())
valor_nominal_total = float(df["VALOR_TOTAL_CUANTIA"].sum())

df_pot = df[df["ESCENARIO_2026"] == "POTENCIAL_ORDINARIA_2026"]
entidades_potenciales = int(df_pot["NOMBRE_ENTIDAD"].nunique())
procesos_potenciales = int(df_pot["CANTIDAD_PROCESOS"].sum())

entidades_s2 = int(df[df["TIENE_PUBLICACIONES_SECOP2"] == "Sí"]["NOMBRE_ENTIDAD"].nunique())
pct_entidades_s2 = (entidades_s2 / total_entidades * 100.0) if total_entidades > 0 else 0.0

# ── HEADER PRINCIPAL ──────────────────────────────────────────────────────
st.markdown(f"""
<div class="main-header">
    <div class="color-strip"></div>
    <h1>🏛️ Base Maestra Oficial – Estrategia de Despliegue SECOP II (2026)</h1>
    <p>Radiografía integral del 100% de la contratación en SECOP I (2023–2025), homologación multicapa con SECOP II, conectividad MinTIC (3T-2025) y categorización CGN (Ley 617)</p>
    <span class="tag">📅 Vigencias 2023–2025</span>
    <span class="tag">🏢 Subdirección EMAE & IDT</span>
    <span class="tag">📋 {total_procesos:,} procesos seleccionados ({len(df):,} registros agrupados)</span>
    <span class="tag">🏛️ {total_entidades:,} cuentas de entidades ({total_nits:,} NITs homologados)</span>
</div>
""", unsafe_allow_html=True)

# ── KPIs PRINCIPALES ──────────────────────────────────────────────────────
st.markdown('<div class="section-header">📦 Indicadores Clave del Universo Seleccionado</div>', unsafe_allow_html=True)

k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Total Procesos SECOP I</div>
        <div class="kpi-value">{fmt_numero(total_procesos)}</div>
        <div class="kpi-sub">en {len(df):,} filas agrupadas</div>
    </div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""
    <div class="kpi-card verde">
        <div class="kpi-label">Cuentas de Entidades</div>
        <div class="kpi-value">{fmt_numero(total_entidades)}</div>
        <div class="kpi-sub">{fmt_numero(total_nits)} NITs únicos homologados</div>
    </div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""
    <div class="kpi-card naranja">
        <div class="kpi-label">Cuantía Real (Entidades ID)</div>
        <div class="kpi-value">{fmt_billones(valor_real_total, short=True)}</div>
        <div class="kpi-sub">Excl. errores digitación "No Definido"</div>
    </div>""", unsafe_allow_html=True)
with k4:
    st.markdown(f"""
    <div class="kpi-card rojo">
        <div class="kpi-label">Potenciales Obligadas 2026</div>
        <div class="kpi-value">{fmt_numero(entidades_potenciales)}</div>
        <div class="kpi-sub">{fmt_numero(procesos_potenciales)} proc. ordinarios (TD_01)</div>
    </div>""", unsafe_allow_html=True)
with k5:
    st.markdown(f"""
    <div class="kpi-card morado">
        <div class="kpi-label">Ya Publican en SECOP II</div>
        <div class="kpi-value">{fmt_numero(entidades_s2)}</div>
        <div class="kpi-sub">{pct_entidades_s2:.1f}% de las entidades seleccionadas</div>
    </div>""", unsafe_allow_html=True)

st.markdown(f"""
<div style="margin-top: 0.9rem; padding: 0.8rem 1.2rem; background-color: #FEF9E7; border-left: 4px solid #D98A3C; border-radius: 8px; font-size: 0.83rem; color: #3E546C;">
    <strong>📌 Nota Técnica sobre Cuantía Real vs. Nominal:</strong> La cuantía real de las entidades identificadas en la selección es de <strong>{fmt_billones(valor_real_total)}</strong>. 
    En la fuente original de Datos Abiertos existen 309 filas agrupadas (1.660 procesos) con entidad <em>«No Definido»</em> que suman $620,45 Billones por errores humanos de digitación de ceros en SECOP I (cuantía nominal bruta: {fmt_billones(valor_nominal_total)}). Se conservan las filas para mantener intacto el conteo oficial de los 985.596 procesos.
</div>
""", unsafe_allow_html=True)

# ── ESCENARIOS / SEGMENTOS NORMATIVOS 2026 ────────────────────────────────
st.markdown('<div class="section-header">🔑 Radiografía por Bloque Normativo y Obligatoriedad (2026)</div>', unsafe_allow_html=True)

esc_grp = df.groupby("ESCENARIO_2026", observed=True).agg(
    procesos=("CANTIDAD_PROCESOS", "sum"),
    entidades=("NOMBRE_ENTIDAD", "nunique"),
    nits=("NIT_HOMOLOGADO", lambda s: s[s != "Sin NIT Válido"].nunique()),
    valor=("VALOR_REAL_CUANTIA", "sum"),
)

ec1, ec2, ec3, ec4 = st.columns(4)
esc_cols = [ec1, ec2, ec3, ec4]
esc_order = [
    "POTENCIAL_ORDINARIA_2026",
    "OBLIGADA_PREVIA_ORDINARIA",
    "REGIMEN_ESPECIAL_LEY2195",
    "EXCLUSION_NORMATIVA_TD02",
]
for col_ui, esc_key in zip(esc_cols, esc_order):
    if esc_key in esc_grp.index:
        cnt_p = int(esc_grp.loc[esc_key, "procesos"])
        cnt_e = int(esc_grp.loc[esc_key, "entidades"])
        cnt_n = int(esc_grp.loc[esc_key, "nits"])
        val_e = float(esc_grp.loc[esc_key, "valor"])
    else:
        cnt_p, cnt_e, cnt_n, val_e = 0, 0, 0, 0.0

    color = ESCENARIO_COLORS.get(esc_key, "#6C757D")
    label = ESCENARIO_LABELS.get(esc_key, esc_key)
    pct = cnt_p / total_procesos * 100 if total_procesos > 0 else 0.0
    with col_ui:
        st.markdown(f"""
        <div class="esc-card" style="background:{color};">
            <div class="esc-name">{label}</div>
            <div class="esc-val">{cnt_p:,} <span style="font-size:0.85rem;font-weight:500;">proc.</span></div>
            <div class="esc-sub">🏛️ <b>{cnt_e:,}</b> cuentas ({cnt_n:,} NITs) • <b>{pct:.1f}%</b></div>
            <div class="esc-sub">💰 {fmt_billones(val_e, short=True)} reales</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── GRÁFICOS PRINCIPALES ─────────────────────────────────────────────────
st.markdown('<div class="section-header">📊 Análisis Visual por Segmento, Vigencia y Naturaleza Institucional</div>', unsafe_allow_html=True)

metrica_principal = st.radio(
    "Métrica de análisis visual:",
    ["procesos", "entidades", "valor"],
    format_func=lambda x: {
        "procesos": "📄 N° de Procesos SECOP I",
        "entidades": "🏛️ Cuentas de Entidades Únicas",
        "valor": "💰 Cuantía Real Contratada ($ Billones COP)",
    }[x],
    horizontal=True,
    key="metrica_home",
)

g1, g2 = st.columns([1.05, 1.65])
with g1:
    st.markdown("**Proporción por bloque normativo**")
    st.plotly_chart(chart_dona_escenarios(df, metrica_principal), use_container_width=True, key="dona_esc")

with g2:
    st.markdown("**Evolución anual por vigencia (2023–2025)**")
    st.plotly_chart(
        chart_barras_escenario_vigencia(df, metrica_principal),
        use_container_width=True,
        key="barras_vig",
    )

st.markdown("**Distribución según Naturaleza Institucional (10 Tipologías Oficiales)**")
st.plotly_chart(chart_naturaleza_institucional(df, metrica_principal), use_container_width=True, key="nat_inst_home")

# ── MAPA DE CALOR TERRITORIAL (VISTA RÁPIDA EN HOME) ──────────────────────
st.markdown('<div class="section-header">🔥 Mapa de Calor Territorial: Departamentos y Municipios</div>', unsafe_allow_html=True)

mc1, mc2, mc3 = st.columns([1.2, 1.2, 1.2])
with mc1:
    nivel_mapa_home = st.radio(
        "Nivel geográfico:",
        ["departamentos", "municipios"],
        format_func=lambda x: "🗺️ Por Departamento (33 Deptos)" if x == "departamentos" else "📍 Por Municipio (1.076+ Municipios DIVIPOLA)",
        horizontal=True,
        key="nivel_mapa_home",
    )
with mc2:
    metrica_mapa_home = st.selectbox(
        "Indicador de calor:",
        options=["entidades", "procesos", "valor", "penetracion", "pct_secop2"],
        format_func=lambda x: {
            "entidades": "🏛️ N° de Entidades Únicas",
            "procesos": "📄 N° de Procesos SECOP I",
            "valor": "💰 Cuantía Real Contratada",
            "penetracion": "📡 % Penetración Internet Fijo MinTIC",
            "pct_secop2": "✅ % Entidades que Publican en SECOP II",
        }[x],
        key="met_mapa_home",
    )
with mc3:
    escala_home = st.selectbox(
        "Escala de color:",
        options=[
            "Institucional CCE (Azul-Naranja-Rojo)",
            "Calor Intenso (Amarillo-Naranja-Rojo)",
            "Azul Institucional",
            "Viridis (Alto Contraste)",
        ],
        key="esc_mapa_home",
    )

if nivel_mapa_home == "departamentos":
    geojson_depto = load_geojson_departamentos()
    st.plotly_chart(
        chart_mapa_calor_departamentos(df, geojson_depto, metrica=metrica_mapa_home, escala_nombre=escala_home),
        use_container_width=True,
        key="map_home_depto",
    )
else:
    geojson_mpio = load_geojson_municipios()
    modo_mpio_home = st.radio(
        "Visualización municipal:",
        ["densidad", "coropletico", "burbujas"],
        format_func=lambda x: {
            "densidad": "🔥 Mapa de Calor Continuo (Densidad) + Puntos Municipales",
            "coropletico": "🗺️ Polígonos Municipales (Coroplético DANE)",
            "burbujas": "🔵 Burbujas Georreferenciadas por Municipio",
        }[x],
        horizontal=True,
        key="modo_mpio_home",
    )
    st.plotly_chart(
        chart_mapa_calor_municipios(
            df,
            geojson_mpio=geojson_mpio,
            metrica=metrica_mapa_home,
            modo=modo_mpio_home,
            escala_nombre=escala_home,
        ),
        use_container_width=True,
        key="map_home_mpio",
    )

st.caption("💡 **Tip:** En la página **2_🗺️_Territorial** del menú izquierdo encontrarás el análisis territorial completo con selector directo de departamento para hacer zoom automático a sus municipios, matriz de calor 2D y cruce con Categoría CGN e Internet MinTIC.")

# ── TABLA RESUMEN EJECUTIVA ───────────────────────────────────────────────
with st.expander("📋 Ver tablas de balance oficial por Segmento Normativo y por Vigencia", expanded=True):
    t_seg, t_vig = st.tabs(["📊 Balance por Segmento y Obligatoriedad", "📅 Balance Anual por Vigencia (2023–2025)"])
    with t_seg:
        resumen_seg = (
            df.groupby(["SEGMENTO_NORMATIVO", "ESTADO_OBLIGATORIEDAD"], observed=True)
            .agg(
                Filas_Agrupadas=("CANTIDAD_PROCESOS", "count"),
                Procesos=("CANTIDAD_PROCESOS", "sum"),
                Cuentas_Unicas=("NOMBRE_ENTIDAD", "nunique"),
                NITs_Homologados=("NIT_HOMOLOGADO", lambda s: s[s != "Sin NIT Válido"].nunique()),
                Cuantia_Real=("VALOR_REAL_CUANTIA", "sum"),
                Cuantia_Nominal=("VALOR_TOTAL_CUANTIA", "sum"),
            )
            .reset_index()
            .sort_values("Procesos", ascending=False)
        )
        resumen_seg["% Procesos"] = (resumen_seg["Procesos"] / max(total_procesos, 1) * 100).round(1).astype(str) + "%"
        resumen_seg["Cuantía Real (COP)"] = resumen_seg["Cuantia_Real"].apply(fmt_billones)
        resumen_seg["Cuantía Nominal (COP)"] = resumen_seg["Cuantia_Nominal"].apply(fmt_billones)
        resumen_seg = resumen_seg[[
            "SEGMENTO_NORMATIVO", "ESTADO_OBLIGATORIEDAD", "Procesos", "% Procesos",
            "Cuentas_Unicas", "NITs_Homologados", "Cuantía Real (COP)", "Cuantía Nominal (COP)"
        ]].rename(columns={
            "SEGMENTO_NORMATIVO": "Segmento Normativo",
            "ESTADO_OBLIGATORIEDAD": "Estado de Obligatoriedad",
            "Cuentas_Unicas": "Cuentas Únicas",
            "NITs_Homologados": "NITs Homologados",
        })
        st.dataframe(resumen_seg, use_container_width=True, hide_index=True)

    with t_vig:
        resumen_vig = (
            df.groupby("VIGENCIA", observed=True)
            .agg(
                Filas_Agrupadas=("CANTIDAD_PROCESOS", "count"),
                Procesos=("CANTIDAD_PROCESOS", "sum"),
                Entidades=("NOMBRE_ENTIDAD", "nunique"),
                NITs=("NIT_HOMOLOGADO", lambda s: s[s != "Sin NIT Válido"].nunique()),
                Valor_Real=("VALOR_REAL_CUANTIA", "sum"),
            )
            .reset_index()
            .rename(columns={
                "VIGENCIA": "Vigencia",
                "Filas_Agrupadas": "Filas Agrupadas",
                "Entidades": "Cuentas Entidades",
                "NITs": "NITs Homologados",
                "Valor_Real": "Cuantía Real (COP)",
            })
        )
        resumen_vig["Cuantía Real (COP)"] = resumen_vig["Cuantía Real (COP)"].apply(fmt_billones)
        st.dataframe(resumen_vig, use_container_width=True, hide_index=True)
