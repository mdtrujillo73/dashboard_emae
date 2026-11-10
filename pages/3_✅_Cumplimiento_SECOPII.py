"""
Página: Cumplimiento y Estrategia de Despliegue SECOP II (2026)
Incluye las 6 Rutas Operativas de TD_01B (2.975 entidades potenciales),
seguimiento a Obligadas Previas (2020-2025), Ley 2195/2022 (TD_03) y Exclusiones (TD_02).
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.data_loader import (
    load_data,
    load_td01b,
    render_sidebar_filters,
    fmt_billones,
    fmt_numero,
    RUTA_SHORT_LABELS,
)
from utils.charts import (
    chart_gauge_cumplimiento,
    chart_rutas_despliegue_2026,
    CCE_AZUL,
    CCE_ROJO,
    CCE_NARANJA,
    CCE_MORADO,
    LAYOUT_DEFAULTS,
)

st.set_page_config(page_title="Despliegue & Cumplimiento SECOP II | EMAE", page_icon="✅", layout="wide")

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
.cumpl-card{border-radius:14px;padding:1.2rem 1.4rem;text-align:center;box-shadow:0 4px 18px rgba(0,0,0,0.08);height:100%;}
.cumpl-num{font-size:2.05rem;font-weight:700;line-height:1.1;}
.cumpl-lbl{font-size:0.78rem;font-weight:600;margin-top:0.35rem;opacity:0.9;}
</style>
""", unsafe_allow_html=True)

df_raw = load_data()
df_td1b_raw = load_td01b()
df = render_sidebar_filters(df_raw)

# Sincronizar el directorio TD_01B con las entidades presentes en el filtro actual
entidades_filtradas = set(df["NOMBRE_ENTIDAD"].unique())
df_td1b = df_td1b_raw[df_td1b_raw["NOMBRE_ENTIDAD"].isin(entidades_filtradas)].copy()

st.markdown("# ✅ Estrategia de Despliegue y Cumplimiento SECOP II (2026)")
st.markdown(
    "Ruta operativa para las **2.975 entidades potenciales (`TD_01B`)**, control de entidades obligadas en "
    "**vigencias anteriores (2020–2025)**, bloqueo manual por **Ley 2195 de 2022 (`TD_03`)** y **Exclusiones (`TD_02`)**"
)

# ── KPIs sobre TD_01B (Potenciales Obligadas 2026) ────────────────────────
total_pot = len(df_td1b)
proc_pot_total = int(df_td1b["TOTAL_PROCESOS_ORDINARIOS_S1"].sum()) if not df_td1b.empty else 0

tiene_cuenta_mask = ~df_td1b["NOMBRE_CUENTA_SECOP2"].astype(str).str.startswith("Sin Cuenta") if not df_td1b.empty else pd.Series(dtype=bool)
publica_s2_mask = (df_td1b["PUBLICA_EN_SECOP2"] == "Sí") if not df_td1b.empty else pd.Series(dtype=bool)

ent_con_cuenta = int(tiene_cuenta_mask.sum())
ent_publica_s2 = int(publica_s2_mask.sum())
ent_cuenta_sin_pub = max(0, ent_con_cuenta - ent_publica_s2)
ent_sin_cuenta = max(0, total_pot - ent_con_cuenta)

proc_en_publica_s2 = int(df_td1b.loc[publica_s2_mask, "TOTAL_PROCESOS_ORDINARIOS_S1"].sum()) if not df_td1b.empty else 0
proc_en_con_cuenta = int(df_td1b.loc[tiene_cuenta_mask, "TOTAL_PROCESOS_ORDINARIOS_S1"].sum()) if not df_td1b.empty else 0

pct_con_cuenta = (ent_con_cuenta / total_pot * 100.0) if total_pot > 0 else 0.0
pct_publica_s2 = (ent_publica_s2 / total_pot * 100.0) if total_pot > 0 else 0.0
pct_proc_s2    = (proc_en_publica_s2 / proc_pot_total * 100.0) if proc_pot_total > 0 else 0.0

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""<div class="cumpl-card" style="background:#EBF3FA;">
        <div class="cumpl-num" style="color:#174073;">{total_pot:,}</div>
        <div class="cumpl-lbl" style="color:#174073;">Entidades Potenciales (TD_01B)<br><span style="font-size:0.72rem;">{proc_pot_total:,} procesos ordinarios</span></div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="cumpl-card" style="background:#EAFAF1;">
        <div class="cumpl-num" style="color:#1E8449;">{ent_publica_s2:,}</div>
        <div class="cumpl-lbl" style="color:#1E8449;">Ya Publican en SECOP II ({pct_publica_s2:.1f}%)<br><span style="font-size:0.72rem;">Concentran {proc_en_publica_s2:,} proc. ({pct_proc_s2:.1f}%)</span></div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="cumpl-card" style="background:#FEF9E7;">
        <div class="cumpl-num" style="color:#D98A3C;">{ent_con_cuenta:,}</div>
        <div class="cumpl-lbl" style="color:#9C7238;">Con Cuenta en Directorio SECOP II ({pct_con_cuenta:.1f}%)<br><span style="font-size:0.72rem;">Incluye {ent_cuenta_sin_pub:,} cuentas con 0 procesos</span></div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""<div class="cumpl-card" style="background:#FDEDEC;">
        <div class="cumpl-num" style="color:#D61C38;">{ent_sin_cuenta:,}</div>
        <div class="cumpl-lbl" style="color:#D61C38;">Sin Cuenta Propia en SECOP II<br><span style="font-size:0.72rem;">Requieren creación de cuenta o subcuenta</span></div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Gauges de Preparación para el Despliegue 2026 ─────────────────────────
st.markdown('<div class="section-header">📊 Nivel de Alistamiento en SECOP II de las Entidades Potenciales (TD_01B)</div>', unsafe_allow_html=True)

g1, g2, g3 = st.columns(3)
with g1:
    st.plotly_chart(
        chart_gauge_cumplimiento(pct_con_cuenta, "% Potenciales Registradas en SECOP II", meta=70.9),
        use_container_width=True, key="g1"
    )
with g2:
    st.plotly_chart(
        chart_gauge_cumplimiento(pct_publica_s2, "% Potenciales con Publicaciones Activas", meta=50.0),
        use_container_width=True, key="g2"
    )
with g3:
    st.plotly_chart(
        chart_gauge_cumplimiento(pct_proc_s2, "% Procesos TD_01 en Entidades con SECOP II", meta=69.3),
        use_container_width=True, key="g3"
    )

# ── Las 6 Rutas Operativas de Despliegue 2026 ─────────────────────────────
st.markdown('<div class="section-header">🚀 Las 6 Rutas Operativas de Despliegue 2026 (CLASIFICACION_Y_RUTA_DESPLIEGUE_2026)</div>', unsafe_allow_html=True)

met_ruta = st.radio(
    "Visualizar rutas por:",
    ["entidades", "procesos", "valor"],
    format_func=lambda x: {
        "entidades": "🏛️ N° de Entidades Únicas (TD_01B)",
        "procesos": "📄 N° de Procesos Ordinarios SECOP I",
        "valor": "💰 Cuantía Real ($ Billones COP)",
    }[x],
    horizontal=True,
    key="met_ruta_2026",
)

st.plotly_chart(chart_rutas_despliegue_2026(df_td1b, met_ruta), use_container_width=True, key="chart_rutas")

# ── Pestañas de Gestión Operativa ─────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "📋 1. Directorio TD_01B: Potenciales 2026 (2.975 Entidades)",
    "⚠️ 2. Obligadas Vigencias Anteriores (2020–2025) en SECOP I",
    "🔒 3. Régimen Especial (Ley 2195/2022 - TD_03) & Exclusiones (TD_02)",
])

with tab1:
    st.markdown("#### Directorio Maestro Único de Entidades Potenciales (`TD_01B_LISTA_ENTIDADES`)")
    if not df_td1b.empty:
        f_col1, f_col2 = st.columns([2, 1])
        with f_col1:
            rutas_disp = sorted(df_td1b["CLASIFICACION_Y_RUTA_DESPLIEGUE_2026"].dropna().unique().tolist())
            sel_ruta_tbl = st.selectbox(
                "Filtrar por Ruta de Despliegue 2026:",
                ["Todas las rutas (2.975 entidades)"] + rutas_disp,
                key="sel_ruta_tbl",
            )
        with f_col2:
            sel_pub_tbl = st.radio(
                "Estado de publicación en SECOP II:",
                ["Todas", "Sí publica en SECOP II", "No publica en SECOP II"],
                horizontal=True,
                key="sel_pub_tbl",
            )

        tbl_td1b = df_td1b.copy()
        if sel_ruta_tbl != "Todas las rutas (2.975 entidades)":
            tbl_td1b = tbl_td1b[tbl_td1b["CLASIFICACION_Y_RUTA_DESPLIEGUE_2026"] == sel_ruta_tbl]
        if sel_pub_tbl == "Sí publica en SECOP II":
            tbl_td1b = tbl_td1b[tbl_td1b["PUBLICA_EN_SECOP2"] == "Sí"]
        elif sel_pub_tbl == "No publica en SECOP II":
            tbl_td1b = tbl_td1b[tbl_td1b["PUBLICA_EN_SECOP2"] == "No"]

        cols_show_td1b = [
            "NOMBRE_ENTIDAD", "NIT_SECOP1", "NIT_HOMOLOGADO", "NATURALEZA_INSTITUCIONAL",
            "DEPARTAMENTO", "MUNICIPIO", "CODIGO_DIVIPOLA", "CATEGORIA_CGN",
            "PENETRACION_INTERNET_MINTIC", "RANGO_CONECTIVIDAD_MINTIC",
            "PROCESOS_2023", "PROCESOS_2024", "PROCESOS_2025", "TOTAL_PROCESOS_ORDINARIOS_S1",
            "VALOR_REAL_CUANTIA_S1", "NOMBRE_CUENTA_SECOP2", "PUBLICA_EN_SECOP2",
            "PROCESOS_HISTORICOS_SECOP2", "CLASIFICACION_Y_RUTA_DESPLIEGUE_2026"
        ]
        cols_show_td1b = [c for c in cols_show_td1b if c in tbl_td1b.columns]
        tbl_td1b = tbl_td1b[cols_show_td1b].sort_values("TOTAL_PROCESOS_ORDINARIOS_S1", ascending=False)

        st.caption(f"Mostrando **{len(tbl_td1b):,}** entidades únicas | **{int(tbl_td1b['TOTAL_PROCESOS_ORDINARIOS_S1'].sum()):,}** procesos ordinarios")
        tbl_td1b_vista = tbl_td1b.copy()
        tbl_td1b_vista["VALOR_REAL_CUANTIA_S1"] = tbl_td1b_vista["VALOR_REAL_CUANTIA_S1"].fillna(0).apply(lambda v: f"$ {v:,.0f}")
        st.dataframe(
            tbl_td1b_vista,
            use_container_width=True,
            hide_index=True,
            column_config={
                "VALOR_REAL_CUANTIA_S1": st.column_config.TextColumn("Cuantía Real (COP)", width="medium"),
                "TOTAL_PROCESOS_ORDINARIOS_S1": st.column_config.NumberColumn("Total Procesos S1", format="%d"),
                "PROCESOS_HISTORICOS_SECOP2": st.column_config.NumberColumn("Procesos Hist. S2", format="%d"),
            },
            height=430,
        )
        csv_td1b = tbl_td1b.to_csv(index=False).encode("utf-8-sig")
        st.download_button("⬇️ Descargar Directorio TD_01B (CSV)", csv_td1b, "td_01b_entidades_potenciales_2026.csv", "text/csv")

with tab2:
    st.markdown("#### Entidades Obligadas en Vigencias Anteriores (2020–2025) que Registraron Procesos en SECOP I")
    df_prev = df[df["ESTADO_OBLIGATORIEDAD"] == "Obligada Vigencias Anteriores (2020-2025)"].copy()
    if df_prev.empty:
        st.info("No hay registros de obligadas de vigencias anteriores con los filtros seleccionados.")
    else:
        ent_prev = int(df_prev["NOMBRE_ENTIDAD"].nunique())
        proc_prev = int(df_prev["CANTIDAD_PROCESOS"].sum())
        val_prev = float(df_prev["VALOR_REAL_CUANTIA"].sum())
        st.markdown(
            f"**{ent_prev:,}** cuentas únicas identificadas | **{proc_prev:,}** procesos en SECOP I | "
            f"**{fmt_billones(val_prev)}** en cuantía real"
        )
        tbl_prev = (
            df_prev.groupby([
                "NOMBRE_ENTIDAD", "NIT_HOMOLOGADO", "NATURALEZA_INSTITUCIONAL",
                "DEPARTAMENTO", "MUNICIPIO", "SEGMENTO_NORMATIVO",
                "DETALLE_OBLIGACION_PREVIA", "NOMBRE_ENTIDAD_SECOP2", "TIENE_PUBLICACIONES_SECOP2"
            ], observed=True, dropna=False)
            .agg(
                Procesos_S1=("CANTIDAD_PROCESOS", "sum"),
                Valor_Real=("VALOR_REAL_CUANTIA", "sum"),
                Procesos_Hist_S2=("PROCESOS_HISTORICOS_SECOP2", "max"),
            )
            .reset_index()
            .sort_values("Procesos_S1", ascending=False)
        )
        tbl_prev_vista = tbl_prev.copy()
        tbl_prev_vista["Valor_Real"] = tbl_prev_vista["Valor_Real"].fillna(0).apply(lambda v: f"$ {v:,.0f}")
        st.dataframe(
            tbl_prev_vista,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Valor_Real": st.column_config.TextColumn("Cuantía Real (COP)", width="medium"),
                "Procesos_S1": st.column_config.NumberColumn("Procesos SECOP I", format="%d"),
            },
            height=420,
        )
        csv_prev = tbl_prev.to_csv(index=False).encode("utf-8-sig")
        st.download_button("⬇️ Descargar Obligadas Previas (CSV)", csv_prev, "obligadas_vigencias_anteriores_2020_2025.csv", "text/csv")

with tab3:
    col_re, col_ex = st.columns(2)
    with col_re:
        st.markdown("#### 🔒 Régimen Especial y Fondos de Ley (`TD_03` – Ley 2195/2022 Art. 53)")
        df_re = df[df["SEGMENTO_NORMATIVO"] == "Régimen Especial"]
        st.caption(
            f"**{df_re['NOMBRE_ENTIDAD'].nunique():,}** entidades | "
            f"**{int(df_re['CANTIDAD_PROCESOS'].sum()):,}** procesos | "
            f"**{fmt_billones(df_re['VALOR_REAL_CUANTIA'].sum(), short=True)}**"
        )
        re_nat = (
            df_re.groupby("NATURALEZA_INSTITUCIONAL", observed=True)
            .agg(Entidades=("NOMBRE_ENTIDAD", "nunique"), Procesos=("CANTIDAD_PROCESOS", "sum"))
            .reset_index()
            .sort_values("Procesos", ascending=False)
        )
        st.dataframe(re_nat, use_container_width=True, hide_index=True)

    with col_ex:
        st.markdown("#### ⚖️ Exclusiones Normativas de Circular (`TD_02_EXCLUSIONES`)")
        df_ex = df[df["SEGMENTO_NORMATIVO"] == "Exclusión Normativa (Circular SECOP II)"]
        st.caption(
            f"**{df_ex['NOMBRE_ENTIDAD'].nunique():,}** entidades | "
            f"**{int(df_ex['CANTIDAD_PROCESOS'].sum()):,}** procesos | "
            f"**{fmt_billones(df_ex['VALOR_REAL_CUANTIA'].sum(), short=True)}**"
        )
        ex_tipo = (
            df_ex.groupby("TIPO_EXCLUSION", observed=True)
            .agg(
                Entidades=("NOMBRE_ENTIDAD", "nunique"),
                Procesos=("CANTIDAD_PROCESOS", "sum"),
                Cuantia_Real=("VALOR_REAL_CUANTIA", lambda s: fmt_billones(s.sum(), short=True)),
            )
            .reset_index()
            .sort_values("Procesos", ascending=False)
        )
        st.dataframe(ex_tipo, use_container_width=True, hide_index=True)
