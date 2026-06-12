"""
Página: Análisis por Entidades – Rankings y buscador
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.data_loader import load_data, apply_filters, fmt_billones, fmt_numero
from utils.charts import chart_top_entidades, chart_modalidad, CCE_AZUL, ESCENARIO_LABELS, ESCENARIO_COLORS

st.set_page_config(page_title="Entidades | EMAE Dashboard", page_icon="🏢", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html,[class*="css"]{font-family:'Inter',sans-serif;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#003F7E 0%,#002855 100%);}
[data-testid="stSidebar"] *{color:#fff!important;}
[data-testid="stSidebar"] label{color:#A8C8E8!important;font-size:0.82rem;font-weight:500;text-transform:uppercase;letter-spacing:0.03em;}
.section-header{font-size:1.15rem;font-weight:700;color:#003F7E;border-bottom:3px solid #009B3A;padding-bottom:0.4rem;margin:1.5rem 0 1rem 0;}
.entity-card{background:white;border-radius:14px;padding:1.2rem 1.5rem;box-shadow:0 4px 18px rgba(0,63,126,0.10);border-top:4px solid #003F7E;margin-bottom:0.8rem;}
.entity-card h3{color:#003F7E;font-size:1rem;margin:0 0 0.5rem 0;}
.entity-row{display:flex;gap:1rem;flex-wrap:wrap;margin-top:0.4rem;}
.entity-stat{background:#F0F6FF;border-radius:8px;padding:0.4rem 0.8rem;font-size:0.8rem;color:#003F7E;font-weight:600;}
.badge{display:inline-block;padding:.2rem .7rem;border-radius:999px;font-size:.72rem;font-weight:600;color:white;margin:.1rem;}
</style>
""", unsafe_allow_html=True)

df_raw = load_data()

# Sidebar
with st.sidebar:
    st.markdown("## 🏛️ EMAE – SECOPI")
    st.markdown("**(Versión Actualizada)**", unsafe_allow_html=True)
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

    if "MODALIDAD_CONTRATACION" in df_raw.columns:
        modalidades_disp = sorted(df_raw["MODALIDAD_CONTRATACION"].dropna().unique().tolist())
    else:
        modalidades_disp = []
    sel_modalidad = st.multiselect("Modalidad de Contratación", ["Todas"] + modalidades_disp, default=["Todas"])

df = apply_filters(df_raw, sel_vigencia, sel_depto, sel_escenario, sel_regimen, sel_modalidad)

st.markdown("# 🏢 Análisis por Entidades")
st.markdown(f"Mostrando **{len(df):,}** contratos de **{df['NOMBRE_ENTIDAD_SECOPI'].nunique():,}** entidades")

# ── BUSCADOR DE ENTIDAD ────────────────────────────────────────────────────
st.markdown('<div class="section-header">🔍 Ficha de Entidad</div>', unsafe_allow_html=True)

entidades_lista = sorted(df["NOMBRE_ENTIDAD_SECOPI"].dropna().unique().tolist())
entidad_sel = st.selectbox("Buscar entidad:", ["— Seleccione una entidad —"] + entidades_lista)

if entidad_sel != "— Seleccione una entidad —":
    ent_df = df[df["NOMBRE_ENTIDAD_SECOPI"] == entidad_sel]
    esc = ent_df["ESCENARIO_REPORTE_FINAL"].mode().iloc[0] if not ent_df.empty else "N/D"
    reg = ent_df["REGIMEN_CLASIFICADO_FINAL"].mode().iloc[0] if not ent_df.empty else "N/D"
    nit = ent_df["NIT_ENTIDAD_SECOPI"].iloc[0] if not ent_df.empty else "N/D"
    depto = ent_df[col_depto].mode().iloc[0] if not ent_df.empty else "N/D"
    total_c = len(ent_df)
    total_v = ent_df["VALOR_CONTRATO_CON_ADICIONES"].sum()
    aparece = ent_df.get("APARECE_SECOPI_CIRCULAR_FINAL", pd.Series(dtype=str)).mode()
    aparece_str = aparece.iloc[0] if not aparece.empty else "N/D"
    cruce = ent_df.get("TIENE_CRUCE_SECOPII_VALIDADO_FINAL", pd.Series(dtype=str)).mode()
    cruce_str = cruce.iloc[0] if not cruce.empty else "N/D"
    color_esc = ESCENARIO_COLORS.get(esc, "#6C757D")
    label_esc = ESCENARIO_LABELS.get(esc, esc)

    f1, f2 = st.columns([2, 1])
    with f1:
        st.markdown(f"""
        <div class="entity-card">
            <h3>🏛️ {entidad_sel}</h3>
            <span class="badge" style="background:{color_esc};">{label_esc}</span>
            <span class="badge" style="background:#003F7E;">{reg}</span>
            <div class="entity-row">
                <div class="entity-stat">📋 NIT: {nit}</div>
                <div class="entity-stat">🗺️ {depto}</div>
                <div class="entity-stat">📄 {total_c:,} contratos</div>
                <div class="entity-stat">💰 {fmt_billones(total_v)}</div>
                <div class="entity-stat">🔗 SECOP II: {aparece_str}</div>
                <div class="entity-stat">✅ Cruce validado: {cruce_str}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with f2:
        vig_ent = ent_df.groupby("VIGENCIA", observed=True).size().reset_index(name="contratos")
        if not vig_ent.empty:
            import plotly.express as px
            fig_vig = px.bar(vig_ent, x="VIGENCIA", y="contratos",
                             color_discrete_sequence=[CCE_AZUL],
                             labels={"contratos": "Contratos", "VIGENCIA": "Año"})
            fig_vig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                   margin=dict(l=10,r=10,t=30,b=10), height=200,
                                   font=dict(family="Inter, Arial"))
            st.plotly_chart(fig_vig, use_container_width=True, key="vig_ent")

# ── TOPS ──────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">🏆 Rankings de Entidades</div>', unsafe_allow_html=True)

n_top = st.slider("Número de entidades a mostrar:", 5, 30, 20, key="n_top")
t1, t2 = st.columns(2)

with t1:
    st.markdown("**Por número de contratos**")
    st.plotly_chart(chart_top_entidades(df, n_top, "contratos"), use_container_width=True, key="top_c")

with t2:
    st.markdown("**Por valor contratado**")
    st.plotly_chart(chart_top_entidades(df, n_top, "valor"), use_container_width=True, key="top_v")

# ── MODALIDAD ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📑 Modalidad de Contratación</div>', unsafe_allow_html=True)

m1, m2 = st.columns(2)
with m1:
    st.markdown("**Distribución por modalidad (Top 10)**")
    st.plotly_chart(chart_modalidad(df, "pie"), use_container_width=True, key="mod_pie")

with m2:
    st.markdown("**Comparativo modalidades**")
    st.plotly_chart(chart_modalidad(df, "bar"), use_container_width=True, key="mod_bar")

# ── TABLA DESCARGABLE ─────────────────────────────────────────────────────
st.markdown('<div class="section-header">📋 Directorio de Entidades</div>', unsafe_allow_html=True)

cols_dir = ["NOMBRE_ENTIDAD_SECOPI", "NIT_ENTIDAD_SECOPI", col_depto, "MUNICIPIO_SECOPI",
            "ESCENARIO_REPORTE_FINAL", "REGIMEN_CLASIFICADO_FINAL",
            "DEBE_REPORTAR_SEGUN_CIRCULAR_FINAL", "APARECE_SECOPI_CIRCULAR_FINAL"]
cols_dir = [c for c in cols_dir if c in df.columns]

directorio = (df.groupby([c for c in cols_dir if c in df.columns], observed=True, dropna=False)
               .agg(Contratos=("UID","count"), Valor=("VALOR_CONTRATO_CON_ADICIONES","sum"))
               .reset_index()
               .sort_values("Contratos", ascending=False))

col_search, col_dl = st.columns([3, 1])
with col_search:
    filtro_txt = st.text_input("🔎 Filtrar tabla por nombre o NIT:", "")
with col_dl:
    st.write("")
    csv = directorio.to_csv(index=False).encode("utf-8-sig")
    st.download_button("⬇️ Descargar CSV", csv, "directorio_entidades.csv", "text/csv")

if filtro_txt:
    mask = directorio["NOMBRE_ENTIDAD_SECOPI"].str.contains(filtro_txt, case=False, na=False)
    if "NIT_ENTIDAD_SECOPI" in directorio.columns:
        mask |= directorio["NIT_ENTIDAD_SECOPI"].astype(str).str.contains(filtro_txt, case=False, na=False)
    directorio = directorio[mask]

st.dataframe(
    directorio,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Valor": st.column_config.NumberColumn("Valor Contratado (COP)", format="$ {:,.0f}"),
        "Contratos": st.column_config.NumberColumn("N° Contratos", format="%d"),
        "ESCENARIO_REPORTE_FINAL": st.column_config.TextColumn("Escenario"),
    },
    height=400,
)
