"""
Cargador de datos para el Dashboard EMAE – SECOPI 2023-2025
Utiliza Parquet como caché para tiempos de carga ultra-rápidos.
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

# ── Rutas ──────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent.parent  # Directorio raíz del repositorio (dashboard_emae)
PARQUET    = BASE_DIR / "emae_base_estrella.parquet"
EXCEL_PATH = BASE_DIR / "EMAE.BASE_FINAL_ANALISIS_SECOPI_2023_2025_MINTIC_T4_DASHBOARD_V3.xlsx"
SHEET_NAME = "_EMAE_ _BASE_FINAL_ANALISIS_SEC"

# DTYPEs correctos para el Excel (NITs pueden traer guión: "890801149-5")
DTYPE_MAP = {
    "UID": str,
    "NUMERO_CONSTANCIA": str,
    "NUMERO_PROCESO": str,
    "NUMERO_CONTRATO": str,
    "NIT_ENTIDAD_SECOPI": str,
    "CODIGO_ENTIDAD_SECOPI": str,
    "NIT_ENTIDAD_SECOPI_NORM": str,
    "CODIGO_ENTIDAD_SECOPI_NORM": str,
    "NIT_SECOPI_OBLIGADA": str,
    "CODI_ENTI_SECOPI_OBLIGADA": str,
    "CODIGO_DANE_MUNICIPIO": str,
}

# Columnas de valor monetario a convertir a numérico
VALUE_COLS = [
    "CUANTIA_PROCESO",
    "CUANTIA_CONTRATO",
    "VALOR_TOTAL_ADICIONES",
    "VALOR_CONTRATO_CON_ADICIONES",
]

# Etiquetas legibles para los escenarios
ESCENARIO_LABELS = {
    "OBLIGADA_CIRCULAR_Y_LEY80":          "Obligada SECOP II + Ley 80",
    "OBLIGADA_CIRCULAR_PERO_NO_LEY80":    "Obligada SECOP II + Rég. Especial",
    "NO_CIRCULAR_PERO_LEY80":             "No Obligada + Ley 80",
    "NO_CIRCULAR_NO_LEY80":               "No Obligada + Rég. Especial",
}

ESCENARIO_COLORS = {
    "OBLIGADA_CIRCULAR_Y_LEY80":          "#C0392B",   # rojo
    "OBLIGADA_CIRCULAR_PERO_NO_LEY80":    "#E67E22",   # naranja
    "NO_CIRCULAR_PERO_LEY80":             "#F1C40F",   # amarillo
    "NO_CIRCULAR_NO_LEY80":               "#27AE60",   # verde
}

# ── Carga principal ─────────────────────────────────────────────────────────

@st.cache_resource(show_spinner="⏳ Cargando base de datos EMAE...", ttl=3600)
def load_data() -> pd.DataFrame:
    """
    Carga la base estrella desde Parquet (preferido) o desde Excel como fallback.
    Aplica limpieza mínima: fechas, valores numéricos, categorías.
    (Cache invalidation trigger v6)
    """
    if PARQUET.exists():
        df = pd.read_parquet(PARQUET, engine="pyarrow")
    else:
        st.warning("⚠️ Archivo Parquet no encontrado. Cargando desde Excel (puede tardar varios minutos)...")
        df = pd.read_excel(EXCEL_PATH, sheet_name=SHEET_NAME, dtype=DTYPE_MAP)
        df.to_parquet(PARQUET, index=False)

    df = _clean(df)
    
    import gc
    gc.collect()
    
    return df


def _clean(df: pd.DataFrame) -> pd.DataFrame:
    """Limpieza y tipado post-carga."""

    # 🚀 DROPPING DEAD WEIGHT: Liberar más de 600MB de RAM eliminando columnas de texto gigante que no se grafican
    unused_heavy_cols = [
        "DETALLE_OBJETO_CONTRATAR", 
        "OBJETO_CONTRATO_FIRMA", 
        "OBJETO_A_CONTRATAR",
        "NUMERO_CONSTANCIA",
        "NUMERO_PROCESO",
        "NUMERO_CONTRATO"
    ]
    cols_to_drop = [c for c in unused_heavy_cols if c in df.columns]
    df.drop(columns=cols_to_drop, inplace=True)

    # Valores monetarios → numérico (filtrar centinelas: 999_999_999_999_999)
    SENTINEL = 999_999_999_999_999
    for col in VALUE_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            df[col] = df[col].where(df[col] < SENTINEL, other=pd.NA)

    # Fechas
    for col in ["FECHA_FIRMA_CONTRATO", "FECHA_CARGUE_SECOP"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)

    # VIGENCIA como texto para filtros
    if "VIGENCIA" in df.columns:
        df["VIGENCIA"] = df["VIGENCIA"].astype(str).str.replace(r"\.0$", "", regex=True)

    # Etiqueta legible del escenario
    if "ESCENARIO_REPORTE_FINAL" in df.columns:
        df["ESCENARIO_LABEL"] = df["ESCENARIO_REPORTE_FINAL"].map(ESCENARIO_LABELS).fillna(df["ESCENARIO_REPORTE_FINAL"])

    # Penetración internet → float
    if "PENETRACION_INTERNET_FIJO" in df.columns:
        df["PENETRACION_INTERNET_FIJO"] = pd.to_numeric(df["PENETRACION_INTERNET_FIJO"], errors="coerce")

    # Unificación robusta de modalidades
    if "MODALIDAD_CONTRATACION" in df.columns:
        def unify_mod(m):
            if not isinstance(m, str): return m
            m = m.upper()
            if "DIRECTA" in m: return "Contratación Directa"
            if "MINIMA" in m or "MÍNIMA" in m: return "Mínima Cuantía"
            if "ABREVIADA" in m: return "Selección Abreviada"
            if "OBRA" in m: return "Licitación Pública"
            if "LICITACION" in m or "LICITACIÓN" in m: return "Licitación Pública"
            if "CONCURSO" in m or "MERITOS" in m or "MÉRITOS" in m or "MeRITOS" in m: return "Concurso de Méritos"
            if "SUBASTA" in m: return "Subasta"
            if "ESPECIAL" in m: return "Régimen Especial"
            if "CONVENIO" in m or "DOS PARTES" in m: return "Convenios"
            return m.title()
        
        df["MODALIDAD_CONTRATACION"] = df["MODALIDAD_CONTRATACION"].apply(unify_mod)

    # Corrección global RÁPIDA de tildes (usando mapa de valores únicos para no congelar la carga)
    cols_to_fix = ["NOMBRE_ENTIDAD_SECOPI", "REGIMEN_CLASIFICADO_FINAL", "MUNICIPIO_SECOPI", "DEPARTAMENTO_SECOPI", "DEPARTAMENTO_MINTIC"]
    
    import re
    def fix_encoding(text):
        if not isinstance(text, str): return text
        t = text
        # Solo corregir vocales si están precedidas por al menos DOS mayúsculas
        # Esto previene dañar palabras como "Ley" -> "LÉy"
        t = re.sub(r'([A-ZÑ]{2,})a', r'\1Á', t)
        t = re.sub(r'([A-ZÑ]{2,})e', r'\1É', t)
        t = re.sub(r'([A-ZÑ]{2,})i', r'\1Í', t)
        t = re.sub(r'([A-ZÑ]{2,})o', r'\1Ó', t)
        t = re.sub(r'([A-ZÑ]{2,})u', r'\1Ú', t)
        
        # Correcciones explícitas con word boundaries para evitar dobles reemplazos
        t = re.sub(r'\bNARIO\b', 'NARIÑO', t)
        t = re.sub(r'\bBOYAC\b', 'BOYACÁ', t)
        t = re.sub(r'\bBOLVAR\b', 'BOLÍVAR', t)
        t = re.sub(r'\bCRDOBA\b', 'CÓRDOBA', t)
        t = re.sub(r'\bATLNTICO\b', 'ATLÁNTICO', t)
        t = t.replace('BOGOT D.C.', 'BOGOTÁ D.C.')
        t = re.sub(r'\bCHOC\b', 'CHOCÓ', t)
        t = re.sub(r'\bGUAINA\b', 'GUAINÍA', t)
        t = re.sub(r'\bVAUPS\b', 'VAUPÉS', t)
        t = re.sub(r'\bQUINDO\b', 'QUINDÍO', t)
        
        # Limpieza de seguridad final
        t = t.replace('ÁÁ', 'Á').replace('ÉÉ', 'É').replace('ÍÍ', 'Í').replace('ÓÓ', 'Ó').replace('ÚÚ', 'Ú')
        t = t.replace('LÉY', 'LEY').replace('Léy', 'Ley').replace('LÉy', 'Ley')
        return t

    for col in cols_to_fix:
        if col in df.columns:
            uniques = df[col].dropna().unique()
            clean_map = {u: fix_encoding(u) for u in uniques}
            df[col] = df[col].map(clean_map).fillna(df[col])

    # 🚀 Optimización extrema de memoria para Streamlit Cloud (Evitar OOM)
    # Convierte columnas de texto repetitivo en categorías internas
    for col in df.select_dtypes(include=['object']).columns:
        if df[col].nunique() / len(df) < 0.5:
            df[col] = df[col].astype('category')

    return df


# ── Helpers de filtrado ──────────────────────────────────────────────────────

def apply_filters(df: pd.DataFrame, vigencia, departamentos, escenarios, regimen, modalidad=None) -> pd.DataFrame:
    """Aplica los filtros del sidebar al DataFrame."""
    mask = pd.Series(True, index=df.index)

    if vigencia and "Todas" not in vigencia:
        mask &= df["VIGENCIA"].isin(vigencia)

    if departamentos:
        col = "DEPARTAMENTO_MINTIC" if "DEPARTAMENTO_MINTIC" in df.columns else "DEPARTAMENTO_SECOPI"
        mask &= df[col].isin(departamentos)

    if escenarios:
        mask &= df["ESCENARIO_REPORTE_FINAL"].isin(escenarios)

    if regimen and "Todos" not in regimen:
        mask &= df["REGIMEN_CLASIFICADO_FINAL"].isin(regimen)

    if modalidad and "Todas" not in modalidad:
        mask &= df["MODALIDAD_CONTRATACION"].isin(modalidad)

    return df[mask]


# ── Formateadores ────────────────────────────────────────────────────────────

def fmt_billones(value: float) -> str:
    """Formatea valor en billones de COP."""
    if value is None or np.isnan(value):
        return "N/D"
    b = value / 1e12
    return f"${b:,.3f} Billones de Pesos colombianos"


def fmt_numero(value: float) -> str:
    """Formatea número grande con separadores."""
    if value is None or np.isnan(value):
        return "N/D"
    return f"{int(value):,}"
