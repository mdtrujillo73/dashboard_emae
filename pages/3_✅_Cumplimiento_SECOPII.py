"""
Página: Cumplimiento SECOP II – Validación de las 674 entidades obligadas
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.data_loader import load_data, apply_filters, fmt_billones, fmt_numero
from utils.charts import chart_gauge_cumplimiento, CCE_AZUL, CCE_VERDE, CCE_ROJO, LAYOUT_DEFAULTS, ESCENARIO_LABELS

st.set_page_config(page_title="Cumplimiento SECOP II | EMAE", page_icon="✅", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html,[class*="css"]{font-family:'Inter',sans-serif;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#003F7E 0%,#002855 100%);}
[data-testid="stSidebar"] *{color:#fff!important;}
[data-testid="stSidebar"] label{color:#A8C8E8!important;font-size:0.82rem;font-weight:500;text-transform:uppercase;letter-spacing:0.03em;}
.section-header{font-size:1.15rem;font-weight:700;color:#003F7E;border-bottom:3px solid #009B3A;padding-bottom:0.4rem;margin:1.5rem 0 1rem 0;}
.cumpl-card{border-radius:14px;padding:1.2rem 1.5rem;text-align:center;box-shadow:0 4px 18px rgba(0,0,0,0.10);}
.cumpl-num{font-size:2.2rem;font-weight:700;line-height:1;}
.cumpl-lbl{font-size:0.8rem;font-weight:600;margin-top:0.3rem;opacity:0.85;}
.badge-si{background:#009B3A;color:white;padding:.2rem .7rem;border-radius:999px;font-size:.75rem;font-weight:600;}
.badge-no{background:#C0392B;color:white;padding:.2rem .7rem;border-radius:999px;font-size:.75rem;font-weight:600;}
.badge-nd{background:#6C757D;color:white;padding:.2rem .7rem;border-radius:999px;font-size:.75rem;font-weight:600;}
</style>
""", unsafe_allow_html=True)

df_raw = load_data()

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

    if "MODALIDAD_CONTRATACION" in df_raw.columns:
        modalidades_disp = sorted(df_raw["MODALIDAD_CONTRATACION"].dropna().unique().tolist())
    else:
        modalidades_disp = []
    sel_modalidad = st.multiselect("Modalidad de Contratación", ["Todas"] + modalidades_disp, default=["Todas"])

df = apply_filters(df_raw, sel_vigencia, sel_depto, sel_escenario, sel_regimen, sel_modalidad)

st.markdown("# ✅ Cumplimiento SECOP II")
st.markdown("Validación del universo de **674 entidades** obligadas a publicar en SECOP II")

# ── KPIs de cumplimiento ──────────────────────────────────────────────────
col_circular = "ENTIDAD_EN_CIRCULAR_674_FINAL"
col_aparece  = "APARECE_SECOPI_CIRCULAR_FINAL"
col_cruce    = "TIENE_CRUCE_SECOPII_VALIDADO_FINAL"
col_obligada = "DEBE_REPORTAR_SEGUN_CIRCULAR_FINAL"

# Trabajar a nivel de entidad única (no de contrato)
ent_df = df.drop_duplicates(subset=["NIT_ENTIDAD_SECOPI"], keep="first") if "NIT_ENTIDAD_SECOPI" in df.columns else df.drop_duplicates(subset=["NOMBRE_ENTIDAD_SECOPI"], keep="first")

total_ent = len(ent_df)

en_circular = ent_df[ent_df.get(col_circular, pd.Series(dtype=str)) == "SI"].shape[0] if col_circular in ent_df else 0
aparece_s2  = ent_df[ent_df.get(col_aparece, pd.Series(dtype=str)) == "SI"].shape[0] if col_aparece in ent_df else 0
cruce_val   = ent_df[ent_df.get(col_cruce, pd.Series(dtype=str)) == "SI"].shape[0] if col_cruce in ent_df else 0

pct_circular  = (en_circular / total_ent * 100) if total_ent > 0 else 0
pct_aparece   = (aparece_s2 / en_circular * 100) if en_circular > 0 else 0

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""<div class="cumpl-card" style="background:#E8F4FD;">
        <div class="cumpl-num" style="color:#003F7E;">{total_ent:,}</div>
        <div class="cumpl-lbl" style="color:#003F7E;">Entidades en la muestra</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="cumpl-card" style="background:#FEF9E7;">
        <div class="cumpl-num" style="color:#E67E22;">{en_circular:,}</div>
        <div class="cumpl-lbl" style="color:#E67E22;">En universo de 674 obligadas</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="cumpl-card" style="background:#EAFAF1;">
        <div class="cumpl-num" style="color:#009B3A;">{aparece_s2:,}</div>
        <div class="cumpl-lbl" style="color:#009B3A;">Aparecen en SECOP II</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""<div class="cumpl-card" style="background:#FDEDEC;">
        <div class="cumpl-num" style="color:#C0392B;">{en_circular - aparece_s2:,}</div>
        <div class="cumpl-lbl" style="color:#C0392B;">Obligadas SIN presencia SECOP II</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Gauges ────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📊 Indicadores de Cumplimiento</div>', unsafe_allow_html=True)

g1, g2, g3 = st.columns(3)
with g1:
    st.plotly_chart(
        chart_gauge_cumplimiento(pct_circular, "% Entidades en Universo Obligadas"),
        use_container_width=True, key="g1"
    )
with g2:
    st.plotly_chart(
        chart_gauge_cumplimiento(pct_aparece, "% Obligadas con presencia SECOP II"),
        use_container_width=True, key="g2"
    )
with g3:
    pct_cruce = (cruce_val / total_ent * 100) if total_ent > 0 else 0
    st.plotly_chart(
        chart_gauge_cumplimiento(pct_cruce, "% Con cruce SECOP II validado"),
        use_container_width=True, key="g3"
    )

# ── Tabla de cumplimiento ─────────────────────────────────────────────────
st.markdown('<div class="section-header">📋 Tabla de Cumplimiento por Entidad</div>', unsafe_allow_html=True)

if col_circular in df.columns:
    df_circ = df[df[col_circular] == "SI"].copy()
else:
    df_circ = df.copy()

cols_tabla = ["NOMBRE_ENTIDAD_SECOPI", "NIT_ENTIDAD_SECOPI", col_depto,
              col_circular, col_obligada, col_aparece, col_cruce,
              "REGIMEN_CLASIFICADO_FINAL", "ESCENARIO_REPORTE_FINAL"]
cols_tabla = [c for c in cols_tabla if c in df_circ.columns]

tbl = (df_circ.groupby([c for c in cols_tabla], observed=True, dropna=False)
               .agg(Contratos=("UID","count"), Valor=("VALOR_CONTRATO_CON_ADICIONES","sum"))
               .reset_index()
               .sort_values("Contratos", ascending=False))

# Filtro rápido cumplimiento
filt_cumpl = st.radio(
    "Filtrar por estado SECOP II:",
    ["Todas", "Aparecen en SECOP II", "NO aparecen en SECOP II"],
    horizontal=True,
)
if filt_cumpl == "Aparecen en SECOP II" and col_aparece in tbl.columns:
    tbl = tbl[tbl[col_aparece] == "SI"]
elif filt_cumpl == "NO aparecen en SECOP II" and col_aparece in tbl.columns:
    tbl = tbl[tbl[col_aparece] != "SI"]

st.dataframe(
    tbl,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Valor": st.column_config.NumberColumn("Valor (COP)", format="$ {:,.0f}"),
        "Contratos": st.column_config.NumberColumn("N° Contratos", format="%d"),
        col_aparece: st.column_config.TextColumn("¿Aparece SECOP II?"),
        col_cruce: st.column_config.TextColumn("¿Cruce Validado?"),
        col_circular: st.column_config.TextColumn("¿En 674 Obligadas?"),
    },
    height=450,
)

csv = tbl.to_csv(index=False).encode("utf-8-sig")
st.download_button("⬇️ Descargar tabla CSV", csv, "cumplimiento_secop2.csv", "text/csv")

# ── Distribución por tipo de entidad obligada ─────────────────────────────
if "TIPO_OBLIGADA" in df.columns and df["TIPO_OBLIGADA"].notna().sum() > 0:
    st.markdown('<div class="section-header">🏷️ Tipo de Entidad Obligada</div>', unsafe_allow_html=True)
    tipo_counts = (df[df.get(col_circular, pd.Series(dtype=str)) == "SI"]["TIPO_OBLIGADA"]
                     .value_counts().reset_index())
    tipo_counts.columns = ["Tipo", "Count"]
    fig_tipo = px.pie(tipo_counts, names="Tipo", values="Count",
                      color_discrete_sequence=px.colors.sequential.Blues_r,
                      hole=0.4)
    fig_tipo.update_traces(textinfo="label+percent")
    fig_tipo.update_layout(**LAYOUT_DEFAULTS)
    st.plotly_chart(fig_tipo, use_container_width=True, key="tipo_ent")
