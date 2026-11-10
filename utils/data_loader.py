"""
Cargador de datos para el Dashboard EMAE – Estrategia de Despliegue SECOP II (2026)
Vigencias analizadas: 2023-2025 (985.596 procesos en 57.543 registros agrupados | 4.525 entidades)
Utiliza Parquet y GeoJSON locales como caché para tiempos de carga instantáneos.
"""

import json
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

# ── Rutas ──────────────────────────────────────────────────────────────────
BASE_DIR        = Path(__file__).parent.parent  # dashboard_emae/
ROOT_DIR        = BASE_DIR.parent               # Dashboard/
ASSETS_DIR      = BASE_DIR / "assets"

PARQUET_MAIN    = BASE_DIR / "emae_base_estrella.parquet"
PARQUET_TD01B   = BASE_DIR / "emae_td01b_entidades.parquet"
PARQUET_TD01    = BASE_DIR / "emae_td01_potenciales.parquet"
PARQUET_TD02    = BASE_DIR / "emae_td02_exclusiones.parquet"
PARQUET_TD03    = BASE_DIR / "emae_td03_regimen_especial.parquet"

EXCEL_CANDIDATES = [
    ROOT_DIR / "Datos Actualizados" / "Base_Maestra_Despliegue_SECOP_II_2026 (1).xlsx",
    ROOT_DIR / "Datos Actualizados" / "Base_Maestra_Despliegue_SECOP_II_2026.xlsx",
    BASE_DIR / "Base_Maestra_Despliegue_SECOP_II_2026.xlsx",
]

GEOJSON_DEPTO_PATH = ASSETS_DIR / "colombia_departamentos.geojson"
GEOJSON_MPIO_PATH  = ASSETS_DIR / "colombia_municipios.geojson"
DIVIPOLA_COORDS_PATH = ASSETS_DIR / "divipola_coords.json"

# ── Etiquetas y colores de Escenarios 2026 (Segmento + Obligatoriedad) ────
ESCENARIO_LABELS = {
    "POTENCIAL_ORDINARIA_2026":  "Potencial Obligada 2026 – Ordinaria (TD_01)",
    "OBLIGADA_PREVIA_ORDINARIA": "Obligada Vigencias Anteriores (2020–2025)",
    "REGIMEN_ESPECIAL_LEY2195":  "Régimen Especial / Ley 2195 Art. 53 (TD_03)",
    "EXCLUSION_NORMATIVA_TD02":  "Exclusión Normativa Circular SECOP II (TD_02)",
}

ESCENARIO_COLORS = {
    "POTENCIAL_ORDINARIA_2026":  "#D61C38",  # Rojo CCE (Foco Circular 2026)
    "OBLIGADA_PREVIA_ORDINARIA": "#D98A3C",  # Naranja CCE (Seguimiento circulares previas)
    "REGIMEN_ESPECIAL_LEY2195":  "#533965",  # Morado CCE (Bloqueo Manual Uso y Apropiación)
    "EXCLUSION_NORMATIVA_TD02":  "#174073",  # Azul CCE (Exclusiones normativas)
}

RUTA_SHORT_LABELS = {
    "Entidad / Fondo sujeto a Ley 2195 de 2022 (Art. 53) que registró modalidad ordinaria - Verificar Bloqueo Manual Uso y Apropiación":
        "1. Sujeta a Ley 2195/2022 (FSE/ESP/ESE/Fondo) – Bloqueo Manual",
    "Candidata Circular Obligatoriedad 2026 (Ordinaria) + Bloqueo Manual Régimen Especial / Fondos de Ley (Ley 2195/2022)":
        "2. Candidata Circular 2026 + Bloqueo Manual Rég. Especial",
    "Candidata Circular Obligatoriedad 2026 - Fase 1 (Ya tiene cuenta y publica en SECOP II)":
        "3. Candidata Circular 2026 – Fase 1 (Publica en SECOP II)",
    "Candidata Circular Obligatoriedad 2026 - Fase 1B (Tiene cuenta creada en SECOP II sin publicaciones)":
        "4. Candidata Circular 2026 – Fase 1B (Cuenta sin publicaciones)",
    "Candidata Circular Obligatoriedad 2026 - Fase 2 (Comparte NIT Municipal - Requiere creación de subcuenta en SECOP II)":
        "5. Candidata Circular 2026 – Fase 2 (Comparte NIT Municipal)",
    "Candidata Circular Obligatoriedad 2026 - Fase 2 (Sin cuenta en SECOP II - Requiere registro y capacitación)":
        "6. Candidata Circular 2026 – Fase 2 (Sin cuenta en SECOP II)",
}

DPTO_NAME_TO_CODE = {
    "Antioquia": "05",
    "Atlántico": "08",
    "Bogotá D.C.": "11",
    "Bolívar": "13",
    "Boyacá": "15",
    "Caldas": "17",
    "Caquetá": "18",
    "Cauca": "19",
    "Cesar": "20",
    "Córdoba": "23",
    "Cundinamarca": "25",
    "Chocó": "27",
    "Huila": "41",
    "La Guajira": "44",
    "Magdalena": "47",
    "Meta": "50",
    "Nariño": "52",
    "Norte de Santander": "54",
    "Quindío": "63",
    "Risaralda": "66",
    "Santander": "68",
    "Sucre": "70",
    "Tolima": "73",
    "Valle del Cauca": "76",
    "Arauca": "81",
    "Casanare": "85",
    "Putumayo": "86",
    "San Andrés, Providencia y Santa Catalina": "88",
    "Amazonas": "91",
    "Guainía": "94",
    "Guaviare": "95",
    "Vaupés": "97",
    "Vichada": "99",
}


def _fix_divipola(val):
    if pd.isna(val):
        return val
    s = str(val).strip().replace(".0", "")
    if s.isdigit() and len(s) == 4:
        return "0" + s
    return s


def _assign_escenario(df: pd.DataFrame) -> pd.Series:
    seg = df["SEGMENTO_NORMATIVO"].astype(str)
    est = df["ESTADO_OBLIGATORIEDAD"].astype(str)
    conds = [
        (seg == "Contratación Ordinaria (Estatuto General / Selección)") & (est == "Potencial Obligada 2026"),
        (seg == "Contratación Ordinaria (Estatuto General / Selección)") & (est != "Potencial Obligada 2026"),
        (seg == "Régimen Especial"),
    ]
    choices = [
        "POTENCIAL_ORDINARIA_2026",
        "OBLIGADA_PREVIA_ORDINARIA",
        "REGIMEN_ESPECIAL_LEY2195",
    ]
    return pd.Series(np.select(conds, choices, default="EXCLUSION_NORMATIVA_TD02"), index=df.index)


def _find_excel_path() -> Path:
    for p in EXCEL_CANDIDATES:
        if p.exists():
            return p
    return EXCEL_CANDIDATES[0]


# ── Carga de GeoJSON y Coordenadas ─────────────────────────────────────────

@st.cache_resource(show_spinner=False)
def load_geojson_departamentos() -> dict:
    if GEOJSON_DEPTO_PATH.exists():
        return json.loads(GEOJSON_DEPTO_PATH.read_text(encoding="utf-8"))
    return {"type": "FeatureCollection", "features": []}


@st.cache_resource(show_spinner=False)
def load_geojson_municipios() -> dict:
    if GEOJSON_MPIO_PATH.exists():
        return json.loads(GEOJSON_MPIO_PATH.read_text(encoding="utf-8"))
    return {"type": "FeatureCollection", "features": []}


@st.cache_resource(show_spinner=False)
def load_divipola_coords() -> dict:
    if DIVIPOLA_COORDS_PATH.exists():
        return json.loads(DIVIPOLA_COORDS_PATH.read_text(encoding="utf-8"))
    return {"municipios": {}, "departamentos_code": DPTO_NAME_TO_CODE, "departamentos_center": {}}


# ── Carga principal ─────────────────────────────────────────────────────────

@st.cache_resource(show_spinner="⏳ Cargando Base Maestra SECOP II 2026...", ttl=3600)
def load_data() -> pd.DataFrame:
    """
    Carga la sábana maestra `BASE_MAESTRA_SECOP1` (57.543 filas agrupadas | 985.596 procesos)
    desde Parquet (preferido) o desde el Excel oficial en `Datos Actualizados`.
    """
    if PARQUET_MAIN.exists():
        df = pd.read_parquet(PARQUET_MAIN, engine="pyarrow")
        # Verificar que corresponde a la nueva estructura 2026
        if "SEGMENTO_NORMATIVO" in df.columns and "CANTIDAD_PROCESOS" in df.columns:
            return _post_process_main(df)

    excel_path = _find_excel_path()
    df = pd.read_excel(
        excel_path,
        sheet_name="BASE_MAESTRA_SECOP1",
        dtype={
            "CODIGO_DIVIPOLA": str,
            "NIT_ENTIDAD": str,
            "NIT_HOMOLOGADO": str,
            "VIGENCIA": str,
        },
    )
    df_td1b = pd.read_excel(
        excel_path,
        sheet_name="TD_01B_LISTA_ENTIDADES",
        header=3,
        dtype={
            "CODIGO_DIVIPOLA": str,
            "NIT_SECOP1": str,
            "NIT_HOMOLOGADO": str,
        },
    )
    df = _enrich_and_save(df, df_td1b)
    return _post_process_main(df)


@st.cache_resource(show_spinner="⏳ Cargando directorio de entidades potenciales (TD_01B)...", ttl=3600)
def load_td01b() -> pd.DataFrame:
    """
    Carga la hoja `TD_01B_LISTA_ENTIDADES` (2.975 entidades potenciales únicas).
    """
    if PARQUET_TD01B.exists():
        df_td1b = pd.read_parquet(PARQUET_TD01B, engine="pyarrow")
        return _post_process_td01b(df_td1b)

    # Si no existe, disparar load_data() que construye ambos parquets
    _ = load_data()
    if PARQUET_TD01B.exists():
        df_td1b = pd.read_parquet(PARQUET_TD01B, engine="pyarrow")
        return _post_process_td01b(df_td1b)
    return pd.DataFrame()


@st.cache_resource(show_spinner="⏳ Cargando hoja TD_01_POTENCIALES...", ttl=3600)
def load_td01() -> pd.DataFrame:
    """Carga la hoja `TD_01_POTENCIALES` (18.634 filas agrupadas por modalidad)."""
    if PARQUET_TD01.exists():
        return pd.read_parquet(PARQUET_TD01, engine="pyarrow")
    excel_p = _find_excel_path()
    if excel_p.exists():
        return pd.read_excel(excel_p, sheet_name="TD_01_POTENCIALES", header=3)
    return pd.DataFrame()


@st.cache_resource(show_spinner="⏳ Cargando hoja TD_02_EXCLUSIONES...", ttl=3600)
def load_td02() -> pd.DataFrame:
    """Carga la hoja `TD_02_EXCLUSIONES` (1.682 filas exceptuadas normativamente)."""
    if PARQUET_TD02.exists():
        return pd.read_parquet(PARQUET_TD02, engine="pyarrow")
    excel_p = _find_excel_path()
    if excel_p.exists():
        return pd.read_excel(excel_p, sheet_name="TD_02_EXCLUSIONES", header=3)
    return pd.DataFrame()


@st.cache_resource(show_spinner="⏳ Cargando hoja TD_03_REGIMEN_ESPECIAL...", ttl=3600)
def load_td03() -> pd.DataFrame:
    """Carga la hoja `TD_03_REGIMEN_ESPECIAL` (2.425 filas régimen especial / Ley 2195)."""
    if PARQUET_TD03.exists():
        return pd.read_parquet(PARQUET_TD03, engine="pyarrow")
    excel_p = _find_excel_path()
    if excel_p.exists():
        return pd.read_excel(excel_p, sheet_name="TD_03_REGIMEN_ESPECIAL", header=3)
    return pd.DataFrame()


def get_master_excel_path() -> Path:
    """Retorna la ruta al archivo Excel maestro si existe en disco."""
    return _find_excel_path()


def _enrich_and_save(df_bm: pd.DataFrame, df_td1b: pd.DataFrame) -> pd.DataFrame:
    coords_info = load_divipola_coords()
    coords_map = coords_info.get("municipios", {})
    dpto_center_map = coords_info.get("departamentos_center", {})

    df_bm["CODIGO_DIVIPOLA"] = df_bm["CODIGO_DIVIPOLA"].apply(_fix_divipola)
    df_td1b["CODIGO_DIVIPOLA"] = df_td1b["CODIGO_DIVIPOLA"].apply(_fix_divipola)

    ruta_map = df_td1b.set_index("NOMBRE_ENTIDAD")["CLASIFICACION_Y_RUTA_DESPLIEGUE_2026"].to_dict()
    df_bm["CLASIFICACION_Y_RUTA_DESPLIEGUE_2026"] = (
        df_bm["NOMBRE_ENTIDAD"].map(ruta_map).fillna("No aplica (Fuera de TD_01 Potenciales)")
    )

    df_bm["VALOR_REAL_CUANTIA"] = df_bm["VALOR_TOTAL_CUANTIA"].where(
        df_bm["NOMBRE_ENTIDAD"] != "No Definido", 0.0
    )
    df_td1b["VALOR_REAL_CUANTIA_S1"] = df_td1b["VALOR_TOTAL_CUANTIA_S1"].where(
        df_td1b["NOMBRE_ENTIDAD"] != "No Definido", 0.0
    )

    for d in (df_bm, df_td1b):
        d["CODIGO_DIVIPOLA_MAPA"] = d["CODIGO_DIVIPOLA"].replace({"11000": "11001"})
        d["COD_DPTO"] = d["DEPARTAMENTO"].map(DPTO_NAME_TO_CODE)
        d["LATITUD"] = d["CODIGO_DIVIPOLA_MAPA"].map(lambda c: coords_map.get(c, {}).get("lat"))
        d["LONGITUD"] = d["CODIGO_DIVIPOLA_MAPA"].map(lambda c: coords_map.get(c, {}).get("lon"))
        d["LATITUD"] = d["LATITUD"].fillna(d["COD_DPTO"].map(lambda c: dpto_center_map.get(c, {}).get("lat")))
        d["LONGITUD"] = d["LONGITUD"].fillna(d["COD_DPTO"].map(lambda c: dpto_center_map.get(c, {}).get("lon")))

    df_bm["ESCENARIO_2026"] = _assign_escenario(df_bm)

    df_bm.to_parquet(PARQUET_MAIN, index=False)
    df_td1b.to_parquet(PARQUET_TD01B, index=False)
    return df_bm


def _post_process_main(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["VIGENCIA"] = df["VIGENCIA"].astype(str).str.replace(r"\.0$", "", regex=True)
    df["CODIGO_DIVIPOLA"] = df["CODIGO_DIVIPOLA"].apply(_fix_divipola)
    if "CODIGO_DIVIPOLA_MAPA" not in df.columns:
        df["CODIGO_DIVIPOLA_MAPA"] = df["CODIGO_DIVIPOLA"].replace({"11000": "11001"})
    if "COD_DPTO" not in df.columns:
        df["COD_DPTO"] = df["DEPARTAMENTO"].map(DPTO_NAME_TO_CODE)
    if "VALOR_REAL_CUANTIA" not in df.columns:
        df["VALOR_REAL_CUANTIA"] = df["VALOR_TOTAL_CUANTIA"].where(df["NOMBRE_ENTIDAD"] != "No Definido", 0.0)
    if "ESCENARIO_2026" not in df.columns:
        df["ESCENARIO_2026"] = _assign_escenario(df)

    df["ESCENARIO_LABEL"] = df["ESCENARIO_2026"].map(ESCENARIO_LABELS).fillna(df["ESCENARIO_2026"])

    # Modalidad agrupada para lectura ejecutiva manteniendo el campo original en MODALIDAD_DETALLE
    if "MODALIDAD_DETALLE" not in df.columns and "MODALIDAD_CONTRATACION" in df.columns:
        df["MODALIDAD_DETALLE"] = df["MODALIDAD_CONTRATACION"].astype(str)

        def unify_mod(m):
            if not isinstance(m, str):
                return m
            u = m.upper()
            if "MÍNIMA" in u or "MINIMA" in u:
                return "Mínima Cuantía"
            if "DIRECTA" in u:
                return "Contratación Directa"
            if "ABREVIADA" in u:
                return "Selección Abreviada"
            if "LICITACIÓN" in u or "LICITACION" in u:
                return "Licitación Pública"
            if "MÉRITOS" in u or "MERITOS" in u or "ARQUITECTÓNICO" in u:
                return "Concurso de Méritos"
            if "SUBASTA" in u:
                return "Subasta"
            if "ESPECIAL" in u:
                return "Régimen Especial"
            if "CONVENIO" in u or "DOS PARTES" in u:
                return "Convenios (>2 partes)"
            if "ASOCIACIÓN PÚBLICO" in u or "INICIATIVA PRIVADA" in u:
                return "Asociación Público-Privada (APP)"
            return m

        df["MODALIDAD_AGRUPADA"] = df["MODALIDAD_CONTRATACION"].apply(unify_mod)

    return df


def _post_process_td01b(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["CODIGO_DIVIPOLA"] = df["CODIGO_DIVIPOLA"].apply(_fix_divipola)
    if "CODIGO_DIVIPOLA_MAPA" not in df.columns:
        df["CODIGO_DIVIPOLA_MAPA"] = df["CODIGO_DIVIPOLA"].replace({"11000": "11001"})
    if "COD_DPTO" not in df.columns:
        df["COD_DPTO"] = df["DEPARTAMENTO"].map(DPTO_NAME_TO_CODE)
    if "VALOR_REAL_CUANTIA_S1" not in df.columns:
        df["VALOR_REAL_CUANTIA_S1"] = df["VALOR_TOTAL_CUANTIA_S1"].where(df["NOMBRE_ENTIDAD"] != "No Definido", 0.0)
    df["RUTA_CORTA"] = df["CLASIFICACION_Y_RUTA_DESPLIEGUE_2026"].map(RUTA_SHORT_LABELS).fillna(
        df["CLASIFICACION_Y_RUTA_DESPLIEGUE_2026"]
    )
    return df


# ── Helpers de filtrado y Sidebar compartido ───────────────────────────────

def apply_filters(
    df: pd.DataFrame,
    vigencia=None,
    departamentos=None,
    escenarios=None,
    naturaleza=None,
    modalidad=None,
    categoria_cgn=None,
    rango_mintic=None,
    publica_secop2=None,
) -> pd.DataFrame:
    """Aplica los filtros seleccionados en el sidebar sobre BASE_MAESTRA_SECOP1."""
    mask = pd.Series(True, index=df.index)

    if vigencia and "Todas" not in vigencia:
        mask &= df["VIGENCIA"].isin([str(v) for v in vigencia])

    if departamentos:
        mask &= df["DEPARTAMENTO"].isin(departamentos)

    if escenarios:
        col_esc = "ESCENARIO_2026" if "ESCENARIO_2026" in df.columns else "SEGMENTO_NORMATIVO"
        mask &= df[col_esc].isin(escenarios)

    if naturaleza and "Todas" not in naturaleza:
        col_nat = "NATURALEZA_INSTITUCIONAL" if "NATURALEZA_INSTITUCIONAL" in df.columns else "REGIMEN_CONTRATACION"
        mask &= df[col_nat].isin(naturaleza)

    if modalidad and "Todas" not in modalidad:
        col_mod = "MODALIDAD_AGRUPADA" if "MODALIDAD_AGRUPADA" in df.columns else "MODALIDAD_CONTRATACION"
        mask &= df[col_mod].isin(modalidad)

    if categoria_cgn and "Todas" not in categoria_cgn and "CATEGORIA_CGN" in df.columns:
        mask &= df["CATEGORIA_CGN"].isin(categoria_cgn)

    if rango_mintic and "Todos" not in rango_mintic and "RANGO_CONECTIVIDAD_MINTIC" in df.columns:
        mask &= df["RANGO_CONECTIVIDAD_MINTIC"].isin(rango_mintic)

    if publica_secop2 and publica_secop2 != "Todas" and "TIENE_PUBLICACIONES_SECOP2" in df.columns:
        mask &= df["TIENE_PUBLICACIONES_SECOP2"] == publica_secop2

    return df[mask]


def render_sidebar_filters(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Renderiza el panel lateral institucional y retorna el DataFrame filtrado."""
    with st.sidebar:
        logo_path = ASSETS_DIR / "escudo.png"
        if logo_path.exists():
            st.image(str(logo_path), use_container_width=True)

        st.markdown("## 🏛️ EMAE – SECOP II (2026)")
        st.markdown("**Colombia Compra Eficiente**")
        st.caption("Subdirección EMAE & IDT")
        st.markdown("---")

        vigencias_disp = sorted(df_raw["VIGENCIA"].dropna().unique().tolist())
        sel_vigencia = st.multiselect(
            "Vigencia",
            options=["Todas"] + vigencias_disp,
            default=["Todas"],
        )

        deptos_disp = sorted([d for d in df_raw["DEPARTAMENTO"].dropna().unique().tolist() if d != "No Determinado"])
        if "No Determinado" in df_raw["DEPARTAMENTO"].unique():
            deptos_disp.append("No Determinado")
        sel_depto = st.multiselect("Departamento", options=deptos_disp, default=[])

        escenarios_disp = [k for k in ESCENARIO_LABELS if k in df_raw["ESCENARIO_2026"].unique()]
        sel_escenario = st.multiselect(
            "Bloque / Escenario 2026",
            options=escenarios_disp,
            format_func=lambda x: ESCENARIO_LABELS.get(x, x),
            default=[],
        )

        nat_disp = sorted(df_raw["NATURALEZA_INSTITUCIONAL"].dropna().unique().tolist())
        sel_naturaleza = st.multiselect(
            "Naturaleza Institucional",
            options=nat_disp,
            default=[],
        )

        col_mod = "MODALIDAD_AGRUPADA" if "MODALIDAD_AGRUPADA" in df_raw.columns else "MODALIDAD_CONTRATACION"
        mod_disp = sorted(df_raw[col_mod].dropna().unique().tolist())
        sel_modalidad = st.multiselect(
            "Modalidad de Contratación",
            options=["Todas"] + mod_disp,
            default=["Todas"],
        )

        with st.expander("⚙️ Filtros Avanzados (CGN / MinTIC / SECOP II)", expanded=False):
            cgn_order = ["Especial", "Primera", "Segunda", "Tercera", "Cuarta", "Quinta", "Sexta"]
            cgn_disp = [c for c in cgn_order if c in df_raw["CATEGORIA_CGN"].unique()]
            sel_cgn = st.multiselect("Categoría CGN (Ley 617)", options=cgn_disp, default=[])

            mintic_disp = sorted(df_raw["RANGO_CONECTIVIDAD_MINTIC"].dropna().unique().tolist())
            sel_mintic = st.multiselect("Rango Conectividad MinTIC", options=mintic_disp, default=[])

            sel_pub_s2 = st.radio(
                "¿Publica actualmente en SECOP II?",
                options=["Todas", "Sí", "No"],
                horizontal=True,
            )

        st.markdown("---")
        total_proc_raw = int(df_raw["CANTIDAD_PROCESOS"].sum())
        total_ent_raw = int(df_raw["NOMBRE_ENTIDAD"].nunique())
        st.caption(f"📊 Universo: **{total_proc_raw:,}** procesos | **{total_ent_raw:,}** entidades")
        st.caption("Base Maestra Despliegue SECOP II • 2026")

    return apply_filters(
        df_raw,
        vigencia=sel_vigencia,
        departamentos=sel_depto,
        escenarios=sel_escenario,
        naturaleza=sel_naturaleza,
        modalidad=sel_modalidad,
        categoria_cgn=sel_cgn,
        rango_mintic=sel_mintic,
        publica_secop2=sel_pub_s2,
    )


# ── Formateadores ────────────────────────────────────────────────────────────

def fmt_billones(value: float, short: bool = False) -> str:
    """Formatea valor en billones o miles de millones de COP."""
    if value is None or pd.isna(value):
        return "N/D"
    b = float(value) / 1e12
    if short:
        if abs(b) >= 0.01:
            return f"${b:,.2f} B"
        mm = float(value) / 1e9
        return f"${mm:,.1f} MM"
    return f"${b:,.2f} Billones COP"


def fmt_numero(value: float) -> str:
    """Formatea número grande con separadores."""
    if value is None or pd.isna(value):
        return "N/D"
    return f"{int(round(value)):,}"
