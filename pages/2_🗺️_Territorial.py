"""
Página: Análisis Territorial – Departamentos, municipios y MinTIC
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.data_loader import load_data, apply_filters, fmt_billones, fmt_numero
from utils.charts import chart_top_departamentos, CCE_AZUL, CCE_VERDE, CCE_CLARO, LAYOUT_DEFAULTS, ESCENARIO_LABELS

st.set_page_config(page_title="Territorial | EMAE Dashboard", page_icon="🗺️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html,[class*="css"]{font-family:'Inter',sans-serif;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#003F7E 0%,#002855 100%);}
[data-testid="stSidebar"] *{color:#fff!important;}
[data-testid="stSidebar"] label{color:#A8C8E8!important;font-size:0.82rem;font-weight:500;text-transform:uppercase;letter-spacing:0.03em;}
.section-header{font-size:1.15rem;font-weight:700;color:#003F7E;border-bottom:3px solid #009B3A;padding-bottom:0.4rem;margin:1.5rem 0 1rem 0;}
.info-box{background:#E8F4FD;border-left:4px solid #003F7E;border-radius:8px;padding:0.8rem 1rem;font-size:0.85rem;color:#003F7E;margin-bottom:1rem;}
</style>
""", unsafe_allow_html=True)

df_raw = load_data()

# Sidebar
with st.sidebar:
    st.markdown("## 🏛️ EMAE – SECOPI")
    st.markdown("---")
    vigencias_disp = sorted(df_raw["VIGENCIA"].dropna().unique().tolist())
    sel_vigencia = st.multiselect("Vigencia", ["Todas"] + vigencias_disp, default=["Todas"])
    col_depto = "DEPARTAMENTO_MINTIC" if "DEPARTAMENTO_MINTIC" in df_raw.columns else "DEPARTAMENTO_SECOPI"
    deptos_disp = sorted(df_raw[col_depto].dropna().unique().tolist())
    sel_depto = st.multiselect("Departamento", deptos_disp, default=[])
    escenarios_disp = [k for k in ESCENARIO_LABELS if k in df_raw["ESCENARIO_REPORTE_FINAL"].unique()]
    sel_escenario = st.multiselect("Escenario", escenarios_disp, format_func=lambda x: ESCENARIO_LABELS.get(x,x), default=[])
    regimenes_disp = sorted(df_raw["REGIMEN_CLASIFICADO_FINAL"].dropna().unique().tolist())
    sel_regimen = st.multiselect("Régimen", regimenes_disp, default=[])

df = apply_filters(df_raw, sel_vigencia, sel_depto, sel_escenario, sel_regimen)

st.markdown("# 🗺️ Análisis Territorial")
st.markdown(f"**{df[col_depto].nunique()}** departamentos | **{df['MUNICIPIO_SECOPI'].nunique():,}** municipios | **{len(df):,}** contratos")

# ── TABS de análisis territorial ─────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📊 Por Departamento", "📍 Por Municipio", "📡 Indicadores MinTIC"])

with tab1:
    st.markdown('<div class="section-header">🏘️ Contratación por Departamento</div>', unsafe_allow_html=True)

    metrica_d = st.radio("Ordenar por:", ["valor", "contratos"],
                         format_func=lambda x: "Valor Contratado" if x == "valor" else "N° de Contratos",
                         horizontal=True, key="met_d")
    n_d = st.slider("Top N departamentos:", 5, 33, 15, key="n_d")

    d1, d2 = st.columns([1.5, 1])
    with d1:
        st.plotly_chart(chart_top_departamentos(df, n_d, metrica_d), use_container_width=True, key="top_d")
    with d2:
        # Tabla detalle departamentos
        depto_agg = (df.groupby(col_depto, observed=True)
                       .agg(
                           Contratos=("UID","count"),
                           Entidades=("NOMBRE_ENTIDAD_SECOPI","nunique"),
                           Valor=("VALOR_CONTRATO_CON_ADICIONES","sum"),
                           Municipios=("MUNICIPIO_SECOPI","nunique"),
                       )
                       .reset_index()
                       .sort_values("Contratos", ascending=False))
        depto_agg.columns = ["Departamento", "Contratos", "Entidades", "Valor (COP)", "Municipios"]
        depto_agg["Valor (COP)"] = depto_agg["Valor (COP)"].apply(fmt_billones)
        st.dataframe(depto_agg, use_container_width=True, hide_index=True, height=400)

    # Escenarios por departamento (Top 10)
    st.markdown('<div class="section-header">Escenarios por departamento (Top 10)</div>', unsafe_allow_html=True)
    top10_d = (df.groupby(col_depto, observed=True).size()
                 .nlargest(10).index.tolist())
    df_top10 = df[df[col_depto].isin(top10_d)]
    grp_esc = (df_top10.groupby([col_depto, "ESCENARIO_REPORTE_FINAL"], observed=True)
                        .size().reset_index(name="contratos"))
    grp_esc["label_esc"] = grp_esc["ESCENARIO_REPORTE_FINAL"].map(ESCENARIO_LABELS).fillna(grp_esc["ESCENARIO_REPORTE_FINAL"])

    from utils.charts import ESCENARIO_COLORS
    fig_esc_d = px.bar(
        grp_esc, x=col_depto, y="contratos", color="label_esc",
        color_discrete_map={v: ESCENARIO_COLORS.get(k,"#6C757D") for k,v in ESCENARIO_LABELS.items()},
        barmode="stack",
        labels={"contratos":"N° Contratos", col_depto:"Departamento", "label_esc":"Escenario"},
    )
    fig_esc_d.update_layout(**LAYOUT_DEFAULTS,
                             xaxis_tickangle=-30,
                             legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig_esc_d, use_container_width=True, key="esc_depto")


with tab2:
    st.markdown('<div class="section-header">📍 Top Municipios</div>', unsafe_allow_html=True)

    metrica_m = st.radio("Ordenar por:", ["contratos", "valor"],
                         format_func=lambda x: "N° de Contratos" if x == "contratos" else "Valor Contratado",
                         horizontal=True, key="met_m")
    n_m = st.slider("Top N municipios:", 5, 50, 20, key="n_m")

    col_mpio = "MUNICIPIO_MINTIC" if "MUNICIPIO_MINTIC" in df.columns else "MUNICIPIO_SECOPI"
    if metrica_m == "contratos":
        top_m = (df.groupby([col_depto, col_mpio], observed=True)
                   .size().reset_index(name="valor")
                   .nlargest(n_m, "valor").sort_values("valor"))
        titulo_x = "N° de Contratos"
    else:
        top_m = (df.groupby([col_depto, col_mpio], observed=True)
                   ["VALOR_CONTRATO_CON_ADICIONES"].sum().reset_index(name="valor")
                   .nlargest(n_m, "valor").sort_values("valor"))
        titulo_x = "Valor Contratado (COP)"

    top_m["mpio_label"] = top_m[col_depto] + " / " + top_m[col_mpio]

    fig_m = go.Figure(go.Bar(
        x=top_m["valor"],
        y=top_m["mpio_label"],
        orientation="h",
        marker=dict(color=top_m["valor"], colorscale=[[0,CCE_CLARO],[1,CCE_AZUL]], showscale=False),
        hovertemplate="<b>%{y}</b><br>" + titulo_x + ": %{x:,}<extra></extra>",
    ))
    fig_m.update_layout(**LAYOUT_DEFAULTS, xaxis_title=titulo_x, height=max(400, n_m*28))
    st.plotly_chart(fig_m, use_container_width=True, key="top_mpio")


with tab3:
    st.markdown('<div class="section-header">📡 Penetración de Internet Fijo (MinTIC)</div>', unsafe_allow_html=True)

    if "PENETRACION_INTERNET_FIJO" not in df.columns or df["PENETRACION_INTERNET_FIJO"].isna().all():
        st.info("ℹ️ Datos de penetración MinTIC no disponibles en la selección actual.")
    else:
        st.markdown('<div class="info-box">📌 Datos incorporados desde MinTIC. Indica la tasa de penetración de internet fijo por municipio, complementando la caracterización territorial de las entidades analizadas.</div>', unsafe_allow_html=True)

        mintic_agg = (df.groupby([col_depto], observed=True)
                        .agg(
                            Penetracion=("PENETRACION_INTERNET_FIJO","mean"),
                            Accesos=("No_ACCESOS_FIJOS_A_INTERNET","mean"),
                            Poblacion=("POBLACION_DANE","mean"),
                            Contratos=("UID","count"),
                            Valor=("VALOR_CONTRATO_CON_ADICIONES","sum"),
                        )
                        .reset_index()
                        .dropna(subset=["Penetracion"]))

        m1, m2 = st.columns(2)
        with m1:
            # Scatter: penetración vs contratos
            fig_sc = px.scatter(
                mintic_agg, x="Penetracion", y="Contratos",
                size="Accesos", color="Contratos",
                hover_name=col_depto,
                color_continuous_scale=[[0, CCE_CLARO], [1, CCE_AZUL]],
                labels={"Penetracion": "Penetración Internet Fijo (%)",
                        "Contratos": "N° de Contratos"},
                title="Penetración Internet vs N° de Contratos",
            )
            fig_sc.update_layout(**LAYOUT_DEFAULTS)
            st.plotly_chart(fig_sc, use_container_width=True, key="scatter_mintic")

        with m2:
            # Top deptos por penetración
            top_pen = mintic_agg.sort_values("Penetracion", ascending=True).tail(15)
            fig_pen = go.Figure(go.Bar(
                x=top_pen["Penetracion"],
                y=top_pen[col_depto],
                orientation="h",
                marker=dict(color=top_pen["Penetracion"],
                            colorscale=[[0,CCE_CLARO],[1,CCE_VERDE]], showscale=False),
                hovertemplate="<b>%{y}</b><br>Penetración: %{x:.1f}%<extra></extra>",
            ))
            fig_pen.update_layout(**LAYOUT_DEFAULTS, xaxis_title="Penetración Internet (%)",
                                   title="Top 15 – Penetración Internet Fijo", height=420)
            st.plotly_chart(fig_pen, use_container_width=True, key="pen_bar")

        # Tabla MinTIC
        st.markdown("**Detalle por departamento**")
        mintic_show = mintic_agg.copy()
        mintic_show.columns = ["Departamento", "Penetración (%)", "Accesos Fijos Prom.", "Población Prom.", "Contratos", "Valor (COP)"]
        mintic_show["Penetración (%)"] = mintic_show["Penetración (%)"].round(2)
        mintic_show["Valor (COP)"] = mintic_show["Valor (COP)"].apply(fmt_billones)
        mintic_show["Contratos"] = mintic_show["Contratos"].apply(lambda x: f"{x:,}")
        st.dataframe(mintic_show.sort_values("Penetración (%)", ascending=False),
                     use_container_width=True, hide_index=True)
