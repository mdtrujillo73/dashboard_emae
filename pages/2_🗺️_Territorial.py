"""
Página: Análisis Territorial – Mapas de Calor (Departamentos y Municipios), CGN Ley 617 y MinTIC 3T-2025
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
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
    chart_top_departamentos,
    chart_mapa_calor_departamentos,
    chart_mapa_calor_municipios,
    chart_matriz_calor_territorial,
    aggregate_departamentos,
    aggregate_municipios,
    CCE_AZUL,
    CCE_ROJO,
    CCE_NARANJA,
    CCE_CLARO,
    LAYOUT_DEFAULTS,
)

st.set_page_config(page_title="Territorial & Mapa de Calor | EMAE", page_icon="🗺️", layout="wide")

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
.info-box{background:#EBF3FA;border-left:4px solid #174073;border-radius:8px;padding:0.85rem 1.1rem;font-size:0.85rem;color:#174073;margin-bottom:1rem;}
</style>
""", unsafe_allow_html=True)

df_raw = load_data()
df = render_sidebar_filters(df_raw)

n_deptos_act = df[df["DEPARTAMENTO"] != "No Determinado"]["DEPARTAMENTO"].nunique()
n_mpios_act = df[df["CODIGO_DIVIPOLA_MAPA"] != "00000"]["CODIGO_DIVIPOLA_MAPA"].nunique()
total_proc = int(df["CANTIDAD_PROCESOS"].sum())
total_ent = int(df["NOMBRE_ENTIDAD"].nunique())

st.markdown("# 🗺️ Análisis Territorial y Mapas de Calor")
st.markdown(
    f"**{n_deptos_act}** departamentos | **{n_mpios_act:,}** municipios (DANE DIVIPOLA) | "
    f"**{total_ent:,}** entidades | **{total_proc:,}** procesos en SECOP I"
)

# ── TABS de análisis territorial ─────────────────────────────────────────
tab_mapa, tab_matriz, tab_ranking, tab_mintic = st.tabs([
    "🔥 Mapa de Calor Geográfico (Deptos y Municipios)",
    "🧩 Matriz de Calor 2D (Cruces)",
    "📊 Rankings Departamentos y Municipios",
    "📡 Conectividad MinTIC (3T-2025) & CGN (Ley 617)",
])

# ═══════════════════════════════════════════════════════════════════════════
# TAB 1: MAPA DE CALOR GEOGRÁFICO (DEPARTAMENTOS Y MUNICIPIOS)
# ═══════════════════════════════════════════════════════════════════════════
with tab_mapa:
    st.markdown('<div class="section-header">🔥 Mapa de Calor Interactivo: Departamentos y Municipios de las Entidades</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="info-box">📌 <b>Georreferenciación Oficial DANE DIVIPOLA:</b> Explora la concentración territorial de las entidades compradoras, sus procesos en SECOP I, cuantías reales, conectividad MinTIC y nivel de adopción de SECOP II tanto a nivel <b>Departamental (33 departamentos)</b> como <b>Municipal (1.076+ municipios)</b>. Selecciona un departamento en el filtro rápido para hacer <b>zoom automático</b> a todos sus municipios.</div>',
        unsafe_allow_html=True,
    )

    c_ctrl1, c_ctrl2, c_ctrl3, c_ctrl4 = st.columns([1.3, 1.2, 1.2, 1.1])
    with c_ctrl1:
        vista_mapa = st.selectbox(
            "Disposición de mapas:",
            options=["dual", "depto", "mpio"],
            format_func=lambda x: {
                "dual": "🔀 Vista Dual (Departamentos + Municipios lado a lado)",
                "depto": "🗺️ Solo Mapa de Calor Departamental (33 Deptos)",
                "mpio": "📍 Solo Mapa de Calor Municipal (1.076+ Municipios)",
            }[x],
            key="vista_mapa_terr",
        )
    with c_ctrl2:
        metrica_calor = st.selectbox(
            "Indicador del Mapa de Calor:",
            options=["entidades", "procesos", "valor", "penetracion", "pct_secop2"],
            format_func=lambda x: {
                "entidades": "🏛️ N° de Entidades Únicas",
                "procesos": "📄 N° de Procesos en SECOP I",
                "valor": "💰 Cuantía Real Contratada",
                "penetracion": "📡 % Penetración Internet Fijo MinTIC",
                "pct_secop2": "✅ % Entidades que Publican en SECOP II",
            }[x],
            key="met_calor_terr",
        )
    with c_ctrl3:
        deptos_lista = sorted([d for d in df["DEPARTAMENTO"].dropna().unique().tolist() if d != "No Determinado"])
        depto_zoom = st.selectbox(
            "🔍 Enfocar Departamento (Zoom Municipal):",
            options=["🇨🇴 Toda Colombia (Vista Nacional)"] + deptos_lista,
            key="depto_zoom_terr",
        )
    with c_ctrl4:
        escala_calor = st.selectbox(
            "Paleta de Calor:",
            options=[
                "Institucional CCE (Azul-Naranja-Rojo)",
                "Calor Intenso (Amarillo-Naranja-Rojo)",
                "Azul Institucional",
                "Viridis (Alto Contraste)",
                "Plasma",
            ],
            key="escala_calor_terr",
        )

    modo_mpio = st.radio(
        "Modo de capa para el Mapa Municipal:",
        options=["densidad", "coropletico", "burbujas"],
        format_func=lambda x: {
            "densidad": "🔥 Mapa de Calor de Densidad + Puntos Municipales (Recomendado)",
            "coropletico": "🗺️ Polígonos Municipales Coropléticos (Límites DANE)",
            "burbujas": "🔵 Burbujas Georreferenciadas por Municipio",
        }[x],
        horizontal=True,
        key="modo_mpio_terr",
    )

    df_mpio_view = df if depto_zoom == "🇨🇴 Toda Colombia (Vista Nacional)" else df[df["DEPARTAMENTO"] == depto_zoom]

    geojson_depto = load_geojson_departamentos()
    geojson_mpio = load_geojson_municipios()

    if vista_mapa == "dual":
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown("#### 🗺️ Mapa de Calor por Departamento")
            st.plotly_chart(
                chart_mapa_calor_departamentos(
                    df_mpio_view if depto_zoom != "🇨🇴 Toda Colombia (Vista Nacional)" else df,
                    geojson_depto,
                    metrica=metrica_calor,
                    escala_nombre=escala_calor,
                ),
                use_container_width=True,
                key="terr_dual_depto",
            )
        with col_m2:
            titulo_m2 = "📍 Mapa de Calor por Municipio" if depto_zoom == "🇨🇴 Toda Colombia (Vista Nacional)" else f"📍 Municipios de {depto_zoom}"
            st.markdown(f"#### {titulo_m2}")
            st.plotly_chart(
                chart_mapa_calor_municipios(
                    df_mpio_view,
                    geojson_mpio=geojson_mpio,
                    metrica=metrica_calor,
                    modo=modo_mpio,
                    escala_nombre=escala_calor,
                ),
                use_container_width=True,
                key="terr_dual_mpio",
            )
    elif vista_mapa == "depto":
        st.plotly_chart(
            chart_mapa_calor_departamentos(
                df_mpio_view if depto_zoom != "🇨🇴 Toda Colombia (Vista Nacional)" else df,
                geojson_depto,
                metrica=metrica_calor,
                escala_nombre=escala_calor,
            ),
            use_container_width=True,
            key="terr_single_depto",
        )
    else:
        st.plotly_chart(
            chart_mapa_calor_municipios(
                df_mpio_view,
                geojson_mpio=geojson_mpio,
                metrica=metrica_calor,
                modo=modo_mpio,
                escala_nombre=escala_calor,
            ),
            use_container_width=True,
            key="terr_single_mpio",
        )

    # Tabla resumen de los municipios en la vista actual
    with st.expander(f"📋 Ver detalle municipal georreferenciado ({depto_zoom})", expanded=False):
        agg_m_tbl = aggregate_municipios(df_mpio_view)
        if not agg_m_tbl.empty:
            agg_m_tbl = agg_m_tbl.sort_values(["entidades", "procesos"], ascending=False)
            show_m = agg_m_tbl[[
                "CODIGO_DIVIPOLA_MAPA", "DEPARTAMENTO", "MUNICIPIO", "categoria_cgn",
                "entidades", "nits_homologados", "procesos", "valor_mm",
                "penetracion_mintic", "pct_secop2"
            ]].rename(columns={
                "CODIGO_DIVIPOLA_MAPA": "DIVIPOLA",
                "DEPARTAMENTO": "Departamento",
                "MUNICIPIO": "Municipio",
                "categoria_cgn": "Categoría CGN",
                "entidades": "Entidades Únicas",
                "nits_homologados": "NITs Homologados",
                "procesos": "Procesos SECOP I",
                "valor_mm": "Cuantía Real ($ Miles de Millones)",
                "penetracion_mintic": "Internet Fijo MinTIC (%)",
                "pct_secop2": "% Entidades en SECOP II",
            })
            show_m["Internet Fijo MinTIC (%)"] = show_m["Internet Fijo MinTIC (%)"].round(2)
            show_m["% Entidades en SECOP II"] = show_m["% Entidades en SECOP II"].round(1)
            show_m["Cuantía Real ($ Miles de Millones)"] = show_m["Cuantía Real ($ Miles de Millones)"].round(2)
            st.dataframe(show_m, use_container_width=True, hide_index=True, height=380)


# ═══════════════════════════════════════════════════════════════════════════
# TAB 2: MATRIZ DE CALOR 2D (DEPARTAMENTO VS DIMENSIÓN)
# ═══════════════════════════════════════════════════════════════════════════
with tab_matriz:
    st.markdown('<div class="section-header">🧩 Matriz de Calor 2D: Departamentos vs. Tipología, Categoría CGN y Conectividad</div>', unsafe_allow_html=True)

    hm1, hm2, hm3 = st.columns(3)
    with hm1:
        dim_matriz = st.selectbox(
            "Cruzar Departamentos contra:",
            options=[
                "NATURALEZA_INSTITUCIONAL",
                "CATEGORIA_CGN",
                "RANGO_CONECTIVIDAD_MINTIC",
                "ESCENARIO_LABEL",
            ],
            format_func=lambda x: {
                "NATURALEZA_INSTITUCIONAL": "🏛️ Naturaleza Institucional (10 Tipologías)",
                "CATEGORIA_CGN": "📊 Categoría Municipal CGN (Ley 617)",
                "RANGO_CONECTIVIDAD_MINTIC": "📡 Rango Conectividad Internet MinTIC",
                "ESCENARIO_LABEL": "🔑 Bloque / Escenario Normativo 2026",
            }[x],
            key="dim_matriz",
        )
    with hm2:
        met_matriz = st.radio(
            "Métrica en celdas:",
            options=["entidades", "procesos", "valor"],
            format_func=lambda x: {
                "entidades": "Entidades Únicas",
                "procesos": "Procesos SECOP I",
                "valor": "Cuantía ($ Miles de Millones)",
            }[x],
            horizontal=True,
            key="met_matriz",
        )
    with hm3:
        top_n_mat = st.slider("Top N Departamentos a mostrar:", 10, 33, 20, key="top_n_mat")

    st.plotly_chart(
        chart_matriz_calor_territorial(df, dim_col=dim_matriz, metrica=met_matriz, top_n=top_n_mat),
        use_container_width=True,
        key="heatmap_2d",
    )


# ═══════════════════════════════════════════════════════════════════════════
# TAB 3: RANKINGS POR DEPARTAMENTO Y MUNICIPIO
# ═══════════════════════════════════════════════════════════════════════════
with tab_ranking:
    st.markdown('<div class="section-header">🏘️ Contratación y Entidades por Departamento</div>', unsafe_allow_html=True)

    metrica_d = st.radio(
        "Ordenar departamentos por:",
        ["entidades", "procesos", "valor"],
        format_func=lambda x: {
            "entidades": "🏛️ N° de Entidades Únicas",
            "procesos": "📄 N° de Procesos SECOP I",
            "valor": "💰 Cuantía Real Contratada",
        }[x],
        horizontal=True,
        key="met_d",
    )
    n_d = st.slider("Top N departamentos:", 5, 33, 18, key="n_d")

    d1, d2 = st.columns([1.35, 1.15])
    with d1:
        st.plotly_chart(chart_top_departamentos(df, n_d, metrica_d), use_container_width=True, key="top_d")
    with d2:
        depto_agg = aggregate_departamentos(df)
        if not depto_agg.empty:
            depto_agg = depto_agg.sort_values(
                "entidades" if metrica_d == "entidades" else ("procesos" if metrica_d == "procesos" else "valor_billones"),
                ascending=False,
            )
            depto_show = depto_agg[[
                "DEPARTAMENTO", "entidades", "nits_homologados", "procesos", "valor_billones", "municipios", "pct_secop2"
            ]].rename(columns={
                "DEPARTAMENTO": "Departamento",
                "entidades": "Entidades",
                "nits_homologados": "NITs",
                "procesos": "Procesos",
                "valor_billones": "Cuantía Real",
                "municipios": "Municipios",
                "pct_secop2": "% en SECOP II",
            })
            depto_show["Cuantía Real"] = depto_show["Cuantía Real"].apply(lambda v: f"${v:,.2f} B")
            depto_show["% en SECOP II"] = depto_show["% en SECOP II"].apply(lambda v: f"{v:.1f}%")
            st.dataframe(depto_show, use_container_width=True, hide_index=True, height=440)

    st.markdown('<div class="section-header">📍 Top Municipios con Mayor Actividad en SECOP I</div>', unsafe_allow_html=True)

    metrica_m = st.radio(
        "Ordenar municipios por:",
        ["entidades", "procesos", "valor"],
        format_func=lambda x: {
            "entidades": "🏛️ N° de Entidades Únicas",
            "procesos": "📄 N° de Procesos SECOP I",
            "valor": "💰 Cuantía Real Contratada",
        }[x],
        horizontal=True,
        key="met_m",
    )
    n_m = st.slider("Top N municipios:", 10, 50, 20, key="n_m")

    mpio_agg = aggregate_municipios(df)
    if not mpio_agg.empty:
        col_sort = {"entidades": "entidades", "procesos": "procesos", "valor": "valor_mm"}[metrica_m]
        titulo_x = {
            "entidades": "N° de Entidades Únicas",
            "procesos": "N° de Procesos SECOP I",
            "valor": "Cuantía Real ($ Miles de Millones COP)",
        }[metrica_m]

        top_m = mpio_agg.nlargest(n_m, col_sort).sort_values(col_sort)
        top_m["mpio_label"] = top_m["DEPARTAMENTO"].astype(str) + " – " + top_m["MUNICIPIO"].astype(str) + " (" + top_m["CODIGO_DIVIPOLA_MAPA"] + ")"

        fig_m = go.Figure(go.Bar(
            x=top_m[col_sort],
            y=top_m["mpio_label"],
            orientation="h",
            marker=dict(color=top_m[col_sort], colorscale=[[0, "#DCE7F3"], [0.6, CCE_AZUL], [1, CCE_ROJO]], showscale=False),
            hovertemplate="<b>%{y}</b><br>" + titulo_x + ": %{x:,}<extra></extra>",
        ))
        fig_m.update_layout(**LAYOUT_DEFAULTS, xaxis_title=titulo_x, height=max(420, n_m * 26))
        st.plotly_chart(fig_m, use_container_width=True, key="top_mpio")


# ═══════════════════════════════════════════════════════════════════════════
# TAB 4: CONECTIVIDAD MINTIC (3T-2025) & CATEGORÍA CGN (LEY 617)
# ═══════════════════════════════════════════════════════════════════════════
with tab_mintic:
    st.markdown('<div class="section-header">📡 Conectividad MinTIC (Boletín 3T-2025) y Categorización Presupuestal CGN (Ley 617)</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="info-box">📌 <b>Cruce Oficial DANE / MinTIC (3T-2025) y Contaduría General de la Nación (CGN):</b> Evalúa la viabilidad técnica en territorio combinando el rango de penetración de Internet fijo del municipio con su Categoría Presupuestal de Ley 617 (donde el <b>79,6%</b> de las entidades potenciales pertenecen a municipios de <b>Categoría Sexta</b>).</div>',
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Distribución de Entidades y Procesos por Categoría CGN (Ley 617)**")
        cgn_order = ["Especial", "Primera", "Segunda", "Tercera", "Cuarta", "Quinta", "Sexta"]
        cgn_grp = (
            df.groupby("CATEGORIA_CGN", observed=True)
            .agg(
                Entidades=("NOMBRE_ENTIDAD", "nunique"),
                Procesos=("CANTIDAD_PROCESOS", "sum"),
                Valor_B=("VALOR_REAL_CUANTIA", lambda s: s.sum() / 1e12),
            )
            .reindex([c for c in cgn_order if c in df["CATEGORIA_CGN"].unique()])
            .reset_index()
        )
        fig_cgn = px.bar(
            cgn_grp,
            x="CATEGORIA_CGN",
            y="Entidades",
            text="Entidades",
            color="CATEGORIA_CGN",
            color_discrete_sequence=[CCE_AZUL, "#245894", "#3E546C", "#533965", "#9C7238", CCE_NARANJA, CCE_ROJO],
            labels={"CATEGORIA_CGN": "Categoría CGN", "Entidades": "Entidades Únicas"},
        )
        fig_cgn.update_traces(texttemplate="%{text:,}", textposition="outside")
        fig_cgn.update_layout(**LAYOUT_DEFAULTS, showlegend=False, height=380)
        st.plotly_chart(fig_cgn, use_container_width=True, key="bar_cgn")

    with c2:
        st.markdown("**Distribución por Rango de Conectividad Internet Fijo (MinTIC 3T-2025)**")
        mintic_grp = (
            df.groupby("RANGO_CONECTIVIDAD_MINTIC", observed=True)
            .agg(
                Entidades=("NOMBRE_ENTIDAD", "nunique"),
                Procesos=("CANTIDAD_PROCESOS", "sum"),
            )
            .sort_index()
            .reset_index()
        )
        fig_rng = px.bar(
            mintic_grp,
            x="RANGO_CONECTIVIDAD_MINTIC",
            y="Entidades",
            text="Entidades",
            color="RANGO_CONECTIVIDAD_MINTIC",
            color_discrete_sequence=[CCE_ROJO, CCE_NARANJA, CCE_AZUL, "#27AE60"],
            labels={"RANGO_CONECTIVIDAD_MINTIC": "Tramo de Conectividad MinTIC", "Entidades": "Entidades Únicas"},
        )
        fig_rng.update_traces(texttemplate="%{text:,}", textposition="outside")
        fig_rng.update_layout(**LAYOUT_DEFAULTS, showlegend=False, height=380)
        st.plotly_chart(fig_rng, use_container_width=True, key="bar_mintic_rng")

    # Scatter departamental: Penetración Internet vs Entidades / Procesos
    depto_mintic = aggregate_departamentos(df)
    if not depto_mintic.empty:
        st.markdown("**Relación Departamental: Penetración de Internet Fijo (%) vs. Entidades y Procesos en SECOP I**")
        fig_sc = px.scatter(
            depto_mintic,
            x="penetracion_mintic",
            y="entidades",
            size="procesos",
            color="pct_secop2",
            hover_name="DEPARTAMENTO",
            text="DEPARTAMENTO",
            color_continuous_scale=[[0, CCE_ROJO], [0.5, CCE_NARANJA], [1, "#27AE60"]],
            labels={
                "penetracion_mintic": "Penetración Internet Fijo MinTIC (%)",
                "entidades": "N° de Entidades Únicas en SECOP I",
                "procesos": "Procesos SECOP I",
                "pct_secop2": "% Publica en SECOP II",
            },
        )
        fig_sc.update_traces(textposition="top center", textfont=dict(size=10))
        fig_sc.update_layout(**LAYOUT_DEFAULTS, height=460)
        st.plotly_chart(fig_sc, use_container_width=True, key="scatter_mintic_depto")
