"""
Página: Bases Maestras Oficiales y Centro de Descargas
Acceso y descarga directa de las 5 hojas técnicas oficiales del modelo de despliegue SECOP II 2026:
- TD_01_POTENCIALES
- TD_01B_LISTA_ENTIDADES
- TD_02_EXCLUSIONES
- TD_03_REGIMEN_ESPECIAL
- BASE_MAESTRA_SECOP1
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.data_loader import (
    load_data,
    load_td01,
    load_td01b,
    load_td02,
    load_td03,
    get_master_excel_path,
    render_sidebar_filters,
    fmt_billones,
    fmt_numero,
    ESCENARIO_LABELS,
    ESCENARIO_COLORS,
)

st.set_page_config(page_title="Bases y Descargas | EMAE Dashboard", page_icon="📥", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html,[class*="css"]{font-family:'Inter',sans-serif;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#174073 0%,#3E546C 100%);}
[data-testid="stSidebar"] *{color:#fff!important;}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stRadio label{color:#FFC000!important;font-size:0.80rem;font-weight:600;text-transform:uppercase;letter-spacing:0.03em;}
.section-header{font-size:1.15rem;font-weight:700;color:#174073;border-bottom:3px solid #D61C38;padding-bottom:0.4rem;margin:1.3rem 0 0.9rem 0;}
.card-kpi{background:white;border-radius:12px;padding:1rem 1.2rem;box-shadow:0 3px 14px rgba(23,64,115,0.08);border-left:5px solid #174073;margin-bottom:0.8rem;}
.card-kpi h4{margin:0;font-size:0.82rem;color:#556987;text-transform:uppercase;letter-spacing:0.04em;}
.card-kpi .val{font-size:1.55rem;font-weight:700;color:#174073;margin:0.25rem 0;}
.card-kpi .sub{font-size:0.75rem;color:#8898AA;margin:0;}
.banner-download{background:linear-gradient(135deg,#174073 0%,#275a96 100%);color:white;border-radius:14px;padding:1.4rem 1.8rem;margin-bottom:1.4rem;box-shadow:0 4px 18px rgba(23,64,115,0.15);}
.banner-download h2{color:white;margin:0 0 0.4rem 0;font-size:1.35rem;}
.banner-download p{margin:0;color:#E3E8EE;font-size:0.90rem;line-height:1.4;}
</style>
""", unsafe_allow_html=True)

# Helper cached for CSV generation
@st.cache_data(show_spinner="⏳ Preparando archivo CSV para descarga...")
def get_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8-sig")


# Carga de la base maestra con filtros globales de barra lateral
df_raw = load_data()
df_sidebar = render_sidebar_filters(df_raw)

# Encabezado institucional
st.markdown("# 📥 Bases Maestras Oficiales y Centro de Descargas")
st.markdown(
    "Consulte, filtre e interactúe directamente con cada una de las **5 hojas técnicas oficiales** del modelo "
    "de despliegue y obligatoriedad SECOP II 2026. Puede descargar cada base en formato **CSV (UTF-8 con BOM)** "
    "para su análisis en Excel o herramientas estadísticas, o el libro maestro consolidado."
)

# ── BANNER DESCARGA LIBRO EXCEL MAESTRO ─────────────────────────────────────────
excel_file_path = get_master_excel_path()
col_ban, col_btn = st.columns([2.4, 1.2])

with col_ban:
    st.markdown(f"""
    <div class="banner-download">
        <h2>📑 Libro Maestro: Base_Maestra_Despliegue_SECOP_II_2026.xlsx</h2>
        <p>
            Contiene el modelo analítico integral con las 5 tablas de decisión, metodologías de priorización DIVIPOLA, 
            cobertura MinTIC, categorías CGN e histórico transaccional SECOP I y II (2023–2025).
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_btn:
    st.write("")
    if excel_file_path.exists():
        try:
            with open(excel_file_path, "rb") as f_ex:
                excel_bytes = f_ex.read()
            size_mb = len(excel_bytes) / (1024 * 1024)
            st.download_button(
                label=f"⬇️ Descargar Libro Completo\n(.xlsx • {size_mb:.1f} MB)",
                data=excel_bytes,
                file_name=excel_file_path.name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                help="Descarga el archivo Excel oficial con todas sus pestañas originales.",
            )
        except Exception as e:
            st.warning(f"No fue posible leer el archivo Excel: {e}")
    else:
        st.info("ℹ️ Libro Excel disponible localmente en el repositorio central de datos.")

st.markdown('<div class="section-header">📂 Explorador y Descarga por Pestaña Oficial</div>', unsafe_allow_html=True)

# ── 5 PESTAÑAS TÉCNICAS ────────────────────────────────────────────────────────
tab_td01, tab_td01b, tab_td02, tab_td03, tab_bm = st.tabs([
    "🎯 TD_01_POTENCIALES",
    "📋 TD_01B_LISTA_ENTIDADES",
    "⚖️ TD_02_EXCLUSIONES",
    "🔒 TD_03_REGIMEN_ESPECIAL",
    "🏛️ BASE_MAESTRA_SECOP1",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1: TD_01_POTENCIALES
# ══════════════════════════════════════════════════════════════════════════════
with tab_td01:
    df_td01 = load_td01()
    st.markdown("### 🎯 TD_01_POTENCIALES – Procesos de Entidades Potenciales Ordinarias")
    st.caption("Detalle de procesos agrupados por vigencia, entidad y modalidad para las entidades priorizadas como potenciales obligadas 2026.")

    if not df_td01.empty:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""<div class="card-kpi"><h4>Filas Agrupadas</h4><div class="val">{len(df_td01):,}</div><div class="sub">Registros vigencia-modalidad</div></div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class="card-kpi" style="border-left-color:#D61C38;"><h4>Entidades Únicas</h4><div class="val">{df_td01['NOMBRE_ENTIDAD'].nunique():,}</div><div class="sub">Cuentas compradoras</div></div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""<div class="card-kpi"><h4>Procesos SECOP I</h4><div class="val">{int(df_td01['CANTIDAD_PROCESOS'].sum()):,}</div><div class="sub">Total transacciones</div></div>""", unsafe_allow_html=True)
        with c4:
            st.markdown(f"""<div class="card-kpi" style="border-left-color:#1E8449;"><h4>Cuantía Real</h4><div class="val">{fmt_billones(df_td01['VALOR_REAL_CUANTIA'].sum(), short=True)}</div><div class="sub">{fmt_billones(df_td01['VALOR_REAL_CUANTIA'].sum())}</div></div>""", unsafe_allow_html=True)

        col_filtro, col_down = st.columns([2.5, 1])
        with col_filtro:
            filtro_td01 = st.text_input("🔎 Filtrar TD_01 por entidad, NIT, municipio o modalidad:", "", key="f_td01")
        with col_down:
            st.write("")
            csv_td01 = get_csv_bytes(df_td01)
            st.download_button(
                label=f"⬇️ Descargar TD_01 (CSV • {len(df_td01):,} filas)",
                data=csv_td01,
                file_name="TD_01_POTENCIALES_2026.csv",
                mime="text/csv",
                use_container_width=True,
                key="btn_dl_td01",
            )

        df_show_01 = df_td01.copy()
        if filtro_td01.strip():
            txt = filtro_td01.strip().lower()
            mask = pd.Series(False, index=df_show_01.index)
            for col_c in ["NOMBRE_ENTIDAD", "NIT_HOMOLOGADO", "MUNICIPIO", "DEPARTAMENTO", "MODALIDAD_CONTRATACION"]:
                if col_c in df_show_01.columns:
                    mask |= df_show_01[col_c].astype(str).str.lower().str.contains(txt, na=False)
            df_show_01 = df_show_01[mask]
            st.caption(f"Coincidencias encontradas: **{len(df_show_01):,}** filas")

        vista_01 = df_show_01.copy()
        if "VALOR_REAL_CUANTIA" in vista_01.columns:
            vista_01["VALOR_REAL_CUANTIA"] = vista_01["VALOR_REAL_CUANTIA"].fillna(0).apply(lambda v: f"$ {v:,.0f}")
        if "VALOR_TOTAL_CUANTIA" in vista_01.columns:
            vista_01["VALOR_TOTAL_CUANTIA"] = vista_01["VALOR_TOTAL_CUANTIA"].fillna(0).apply(lambda v: f"$ {v:,.0f}")
        if "PENETRACION_INTERNET_MINTIC" in vista_01.columns:
            vista_01["PENETRACION_INTERNET_MINTIC"] = vista_01["PENETRACION_INTERNET_MINTIC"].fillna(0).apply(lambda v: f"{v*100:.1f}%")

        st.dataframe(vista_01, use_container_width=True, hide_index=True, height=440)
    else:
        st.warning("No se pudo cargar la hoja TD_01_POTENCIALES.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2: TD_01B_LISTA_ENTIDADES
# ══════════════════════════════════════════════════════════════════════════════
with tab_td01b:
    df_td01b = load_td01b()
    st.markdown("### 📋 TD_01B_LISTA_ENTIDADES – Directorio Maestro de Entidades Potenciales 2026")
    st.caption("Ficha de cada una de las 2.975 entidades potenciales con asignación de su Ruta Operativa de Despliegue 2026 y homologación SECOP II.")

    if not df_td01b.empty:
        c1, c2, c3, c4 = st.columns(4)
        pub_si = int((df_td01b["PUBLICA_EN_SECOP2"] == "Sí").sum()) if "PUBLICA_EN_SECOP2" in df_td01b.columns else 0
        with c1:
            st.markdown(f"""<div class="card-kpi"><h4>Entidades Potenciales</h4><div class="val">{len(df_td01b):,}</div><div class="sub">Universo único priorizado</div></div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class="card-kpi" style="border-left-color:#1E8449;"><h4>Publican en SECOP II</h4><div class="val">{pub_si:,}</div><div class="sub">{pub_si/len(df_td01b)*100:.1f}% de alistamiento</div></div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""<div class="card-kpi"><h4>Procesos SECOP I</h4><div class="val">{int(df_td01b['TOTAL_PROCESOS_ORDINARIOS_S1'].sum()):,}</div><div class="sub">2023–2025</div></div>""", unsafe_allow_html=True)
        with c4:
            st.markdown(f"""<div class="card-kpi" style="border-left-color:#D61C38;"><h4>Cuantía Real S1</h4><div class="val">{fmt_billones(df_td01b['VALOR_REAL_CUANTIA_S1'].sum(), short=True)}</div><div class="sub">{fmt_billones(df_td01b['VALOR_REAL_CUANTIA_S1'].sum())}</div></div>""", unsafe_allow_html=True)

        col_filtro, col_down = st.columns([2.5, 1])
        with col_filtro:
            filtro_td01b = st.text_input("🔎 Filtrar TD_01B por entidad, NIT, ruta de despliegue o municipio:", "", key="f_td01b")
        with col_down:
            st.write("")
            csv_td01b = get_csv_bytes(df_td01b)
            st.download_button(
                label=f"⬇️ Descargar TD_01B (CSV • {len(df_td01b):,} entidades)",
                data=csv_td01b,
                file_name="TD_01B_LISTA_ENTIDADES_2026.csv",
                mime="text/csv",
                use_container_width=True,
                key="btn_dl_td01b",
            )

        df_show_01b = df_td01b.copy()
        if filtro_td01b.strip():
            txt = filtro_td01b.strip().lower()
            mask = pd.Series(False, index=df_show_01b.index)
            for col_c in ["NOMBRE_ENTIDAD", "NIT_SECOP1", "NIT_HOMOLOGADO", "MUNICIPIO", "DEPARTAMENTO", "CLASIFICACION_Y_RUTA_DESPLIEGUE_2026", "NOMBRE_CUENTA_SECOP2"]:
                if col_c in df_show_01b.columns:
                    mask |= df_show_01b[col_c].astype(str).str.lower().str.contains(txt, na=False)
            df_show_01b = df_show_01b[mask]
            st.caption(f"Coincidencias encontradas: **{len(df_show_01b):,}** entidades")

        vista_01b = df_show_01b.copy()
        if "VALOR_REAL_CUANTIA_S1" in vista_01b.columns:
            vista_01b["VALOR_REAL_CUANTIA_S1"] = vista_01b["VALOR_REAL_CUANTIA_S1"].fillna(0).apply(lambda v: f"$ {v:,.0f}")
        if "VALOR_TOTAL_CUANTIA_S1" in vista_01b.columns:
            vista_01b["VALOR_TOTAL_CUANTIA_S1"] = vista_01b["VALOR_TOTAL_CUANTIA_S1"].fillna(0).apply(lambda v: f"$ {v:,.0f}")
        if "PENETRACION_INTERNET_MINTIC" in vista_01b.columns:
            vista_01b["PENETRACION_INTERNET_MINTIC"] = vista_01b["PENETRACION_INTERNET_MINTIC"].fillna(0).apply(lambda v: f"{v*100:.1f}%")

        st.dataframe(vista_01b, use_container_width=True, hide_index=True, height=440)
    else:
        st.warning("No se pudo cargar la hoja TD_01B_LISTA_ENTIDADES.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3: TD_02_EXCLUSIONES
# ══════════════════════════════════════════════════════════════════════════════
with tab_td02:
    df_td02 = load_td02()
    st.markdown("### ⚖️ TD_02_EXCLUSIONES – Exclusiones Normativas Circulares SECOP II")
    st.caption("Procesos y entidades expresamente exceptuadas de obligatoriedad según la normativa (APP, Seguridad y Defensa, etc.).")

    if not df_td02.empty:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""<div class="card-kpi"><h4>Filas Excluidas</h4><div class="val">{len(df_td02):,}</div><div class="sub">Registros de excepción</div></div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class="card-kpi" style="border-left-color:#174073;"><h4>Entidades</h4><div class="val">{df_td02['NOMBRE_ENTIDAD'].nunique():,}</div><div class="sub">Cuentas con exclusión</div></div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""<div class="card-kpi"><h4>Procesos</h4><div class="val">{int(df_td02['CANTIDAD_PROCESOS'].sum()):,}</div><div class="sub">Procesos excluidos</div></div>""", unsafe_allow_html=True)
        with c4:
            st.markdown(f"""<div class="card-kpi" style="border-left-color:#D98A3C;"><h4>Cuantía Real</h4><div class="val">{fmt_billones(df_td02['VALOR_REAL_CUANTIA'].sum(), short=True)}</div><div class="sub">{fmt_billones(df_td02['VALOR_REAL_CUANTIA'].sum())}</div></div>""", unsafe_allow_html=True)

        col_filtro, col_down = st.columns([2.5, 1])
        with col_filtro:
            filtro_td02 = st.text_input("🔎 Filtrar TD_02 por tipo de exclusión, entidad o municipio:", "", key="f_td02")
        with col_down:
            st.write("")
            csv_td02 = get_csv_bytes(df_td02)
            st.download_button(
                label=f"⬇️ Descargar TD_02 (CSV • {len(df_td02):,} filas)",
                data=csv_td02,
                file_name="TD_02_EXCLUSIONES_2026.csv",
                mime="text/csv",
                use_container_width=True,
                key="btn_dl_td02",
            )

        df_show_02 = df_td02.copy()
        if filtro_td02.strip():
            txt = filtro_td02.strip().lower()
            mask = pd.Series(False, index=df_show_02.index)
            for col_c in ["TIPO_EXCLUSION", "NOMBRE_ENTIDAD", "MUNICIPIO", "DEPARTAMENTO", "MODALIDAD_CONTRATACION"]:
                if col_c in df_show_02.columns:
                    mask |= df_show_02[col_c].astype(str).str.lower().str.contains(txt, na=False)
            df_show_02 = df_show_02[mask]
            st.caption(f"Coincidencias encontradas: **{len(df_show_02):,}** filas")

        vista_02 = df_show_02.copy()
        if "VALOR_REAL_CUANTIA" in vista_02.columns:
            vista_02["VALOR_REAL_CUANTIA"] = vista_02["VALOR_REAL_CUANTIA"].fillna(0).apply(lambda v: f"$ {v:,.0f}")
        if "VALOR_TOTAL_CUANTIA" in vista_02.columns:
            vista_02["VALOR_TOTAL_CUANTIA"] = vista_02["VALOR_TOTAL_CUANTIA"].fillna(0).apply(lambda v: f"$ {v:,.0f}")
        if "PENETRACION_INTERNET_MINTIC" in vista_02.columns:
            vista_02["PENETRACION_INTERNET_MINTIC"] = vista_02["PENETRACION_INTERNET_MINTIC"].fillna(0).apply(lambda v: f"{v*100:.1f}%")

        st.dataframe(vista_02, use_container_width=True, hide_index=True, height=440)
    else:
        st.warning("No se pudo cargar la hoja TD_02_EXCLUSIONES.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4: TD_03_REGIMEN_ESPECIAL
# ══════════════════════════════════════════════════════════════════════════════
with tab_td03:
    df_td03 = load_td03()
    st.markdown("### 🔒 TD_03_REGIMEN_ESPECIAL – Régimen Especial / Ley 2195 de 2022 (Art. 53)")
    st.caption("Entidades exceptuadas del Estatuto General (ESP, ESE, Universidades Públicas, Fondos con personería) que requieren bloqueo manual para uso y apropiación.")

    if not df_td03.empty:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""<div class="card-kpi"><h4>Filas Régimen Especial</h4><div class="val">{len(df_td03):,}</div><div class="sub">Registros de seguimiento</div></div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class="card-kpi" style="border-left-color:#533965;"><h4>Entidades</h4><div class="val">{df_td03['NOMBRE_ENTIDAD'].nunique():,}</div><div class="sub">Cuentas régimen especial</div></div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""<div class="card-kpi"><h4>Procesos</h4><div class="val">{int(df_td03['CANTIDAD_PROCESOS'].sum()):,}</div><div class="sub">Transacciones registradas</div></div>""", unsafe_allow_html=True)
        with c4:
            st.markdown(f"""<div class="card-kpi" style="border-left-color:#533965;"><h4>Cuantía Real</h4><div class="val">{fmt_billones(df_td03['VALOR_REAL_CUANTIA'].sum(), short=True)}</div><div class="sub">{fmt_billones(df_td03['VALOR_REAL_CUANTIA'].sum())}</div></div>""", unsafe_allow_html=True)

        col_filtro, col_down = st.columns([2.5, 1])
        with col_filtro:
            filtro_td03 = st.text_input("🔎 Filtrar TD_03 por entidad, naturaleza institucional o municipio:", "", key="f_td03")
        with col_down:
            st.write("")
            csv_td03 = get_csv_bytes(df_td03)
            st.download_button(
                label=f"⬇️ Descargar TD_03 (CSV • {len(df_td03):,} filas)",
                data=csv_td03,
                file_name="TD_03_REGIMEN_ESPECIAL_2026.csv",
                mime="text/csv",
                use_container_width=True,
                key="btn_dl_td03",
            )

        df_show_03 = df_td03.copy()
        if filtro_td03.strip():
            txt = filtro_td03.strip().lower()
            mask = pd.Series(False, index=df_show_03.index)
            for col_c in ["NOMBRE_ENTIDAD", "NATURALEZA_INSTITUCIONAL", "TIPO_ENTIDAD", "MUNICIPIO", "DEPARTAMENTO"]:
                if col_c in df_show_03.columns:
                    mask |= df_show_03[col_c].astype(str).str.lower().str.contains(txt, na=False)
            df_show_03 = df_show_03[mask]
            st.caption(f"Coincidencias encontradas: **{len(df_show_03):,}** filas")

        vista_03 = df_show_03.copy()
        if "VALOR_REAL_CUANTIA" in vista_03.columns:
            vista_03["VALOR_REAL_CUANTIA"] = vista_03["VALOR_REAL_CUANTIA"].fillna(0).apply(lambda v: f"$ {v:,.0f}")
        if "VALOR_TOTAL_CUANTIA" in vista_03.columns:
            vista_03["VALOR_TOTAL_CUANTIA"] = vista_03["VALOR_TOTAL_CUANTIA"].fillna(0).apply(lambda v: f"$ {v:,.0f}")
        if "PENETRACION_INTERNET_MINTIC" in vista_03.columns:
            vista_03["PENETRACION_INTERNET_MINTIC"] = vista_03["PENETRACION_INTERNET_MINTIC"].fillna(0).apply(lambda v: f"{v*100:.1f}%")

        st.dataframe(vista_03, use_container_width=True, hide_index=True, height=440)
    else:
        st.warning("No se pudo cargar la hoja TD_03_REGIMEN_ESPECIAL.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5: BASE_MAESTRA_SECOP1
# ══════════════════════════════════════════════════════════════════════════════
with tab_bm:
    st.markdown("### 🏛️ BASE_MAESTRA_SECOP1 – Sábana Maestra Integral (2023–2025)")
    st.caption("Universo consolidado de contratación en SECOP I con segmentación normativa, escenarios 2026 y métricas DIVIPOLA / MinTIC / CGN.")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="card-kpi"><h4>Registros Agrupados</h4><div class="val">{len(df_raw):,}</div><div class="sub">Filas sábana maestra</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="card-kpi" style="border-left-color:#D61C38;"><h4>Total Procesos S1</h4><div class="val">{int(df_raw['CANTIDAD_PROCESOS'].sum()):,}</div><div class="sub">985.596 transacciones</div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="card-kpi"><h4>Entidades Únicas</h4><div class="val">{df_raw['NOMBRE_ENTIDAD'].nunique():,}</div><div class="sub">3.643 NITs homologados</div></div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="card-kpi" style="border-left-color:#1E8449;"><h4>Cuantía Real S1</h4><div class="val">{fmt_billones(df_raw['VALOR_REAL_CUANTIA'].sum(), short=True)}</div><div class="sub">{fmt_billones(df_raw['VALOR_REAL_CUANTIA'].sum())}</div></div>""", unsafe_allow_html=True)

    col_filtro, col_down = st.columns([2.5, 1])
    with col_filtro:
        filtro_bm = st.text_input("🔎 Filtrar Base Maestra por entidad, NIT, municipio, depto o modalidad:", "", key="f_bm")
    with col_down:
        st.write("")
        csv_bm = get_csv_bytes(df_raw)
        st.download_button(
            label=f"⬇️ Descargar Base Maestra (CSV • {len(df_raw):,} filas)",
            data=csv_bm,
            file_name="BASE_MAESTRA_SECOP1_2023_2025.csv",
            mime="text/csv",
            use_container_width=True,
            key="btn_dl_bm",
        )

    df_show_bm = df_raw.copy()
    if filtro_bm.strip():
        txt = filtro_bm.strip().lower()
        mask = pd.Series(False, index=df_show_bm.index)
        for col_c in ["NOMBRE_ENTIDAD", "NIT_ENTIDAD", "NIT_HOMOLOGADO", "MUNICIPIO", "DEPARTAMENTO", "MODALIDAD_CONTRATACION", "SEGMENTO_NORMATIVO"]:
            if col_c in df_show_bm.columns:
                mask |= df_show_bm[col_c].astype(str).str.lower().str.contains(txt, na=False)
        df_show_bm = df_show_bm[mask]
        st.caption(f"Coincidencias encontradas: **{len(df_show_bm):,}** filas")

    # Muestra de columnas más relevantes para agilidad de renderizado
    cols_pref = [
        "VIGENCIA", "NOMBRE_ENTIDAD", "NIT_HOMOLOGADO", "DEPARTAMENTO", "MUNICIPIO",
        "SEGMENTO_NORMATIVO", "ESTADO_OBLIGATORIEDAD", "MODALIDAD_CONTRATACION",
        "CANTIDAD_PROCESOS", "VALOR_REAL_CUANTIA", "TIENE_PUBLICACIONES_SECOP2",
        "CLASIFICACION_Y_RUTA_DESPLIEGUE_2026",
    ]
    cols_exist = [c for c in cols_pref if c in df_show_bm.columns]
    cols_resto = [c for c in df_show_bm.columns if c not in cols_pref]
    df_render_bm = df_show_bm[cols_exist + cols_resto].copy()

    if "VALOR_REAL_CUANTIA" in df_render_bm.columns:
        df_render_bm["VALOR_REAL_CUANTIA"] = df_render_bm["VALOR_REAL_CUANTIA"].fillna(0).apply(lambda v: f"$ {v:,.0f}")
    if "VALOR_TOTAL_CUANTIA" in df_render_bm.columns:
        df_render_bm["VALOR_TOTAL_CUANTIA"] = df_render_bm["VALOR_TOTAL_CUANTIA"].fillna(0).apply(lambda v: f"$ {v:,.0f}")

    st.dataframe(df_render_bm, use_container_width=True, hide_index=True, height=440)

