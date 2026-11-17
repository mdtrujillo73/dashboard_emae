"""
Página: DESPLIEGUE SECOP 2027-2028 – Potenciales Entidades a Obligar por Índice de Penetración MinTIC
Fuente oficial: 'BASE DE DATOS POTENCIALES ENTIDADES A OBLIGAR.xlsx'
Tres hojas / cohortes:
  1. POTENCIALES 5%   (Penetración >= 5%       | 754 entidades | 356 municipios DIVIPOLA)
  2. POTENCIALES 2%   (Penetración 2% a < 5%   | 752 entidades | 291 municipios DIVIPOLA)
  3. INFERIORES A 2%  (Penetración < 2%        | 505 entidades | 211 municipios DIVIPOLA)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import sys
import importlib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

try:
    import utils.data_loader as dl
    if not hasattr(dl, "load_despliegue_2027_2028"):
        dl = importlib.reload(dl)
except Exception:
    import importlib.util
    spec = importlib.util.spec_from_file_location("utils.data_loader", str(BASE_DIR / "utils" / "data_loader.py"))
    dl = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dl)

load_geojson_departamentos = getattr(dl, "load_geojson_departamentos")
load_geojson_municipios = getattr(dl, "load_geojson_municipios")
fmt_billones = getattr(dl, "fmt_billones")
fmt_numero = getattr(dl, "fmt_numero")


@st.cache_resource(show_spinner="⏳ Cargando Base Despliegue SECOP 2027–2028...", ttl=3600)
def get_data_2027() -> pd.DataFrame:
    if hasattr(dl, "load_despliegue_2027_2028"):
        try:
            df = dl.load_despliegue_2027_2028()
            if not df.empty:
                return df
        except Exception:
            pass
    p = BASE_DIR / "emae_despliegue_2027_2028.parquet"
    if p.exists():
        return pd.read_parquet(p, engine="pyarrow")
    return pd.DataFrame()


@st.cache_data(show_spinner=False)
def to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8-sig")


# ── Configuración de página ───────────────────────────────────────────────
st.set_page_config(
    page_title="Despliegue SECOP 2027-2028 | EMAE Dashboard",
    page_icon="🚀",
    layout="wide",
)

# ── Paleta de colores por Hoja / Libro ────────────────────────────────────
SHEET_META = {
    "POTENCIALES 5%": {
        "label": "🟢 POTENCIALES 5% (Penetración ≥ 5%)",
        "short": "POTENCIALES 5% (≥ 5%)",
        "color": "#1E8449",       # Verde Esmeralda intenso
        "color_light": "#2ECC71",
        "bg_badge": "#EAFAF1",
        "rango_desc": "Índice de Penetración ≥ 5.0% (5.02% a 36.71%)",
        "colorscale": [[0.0, "#D4EFDF"], [0.35, "#52BE80"], [0.7, "#1E8449"], [1.0, "#0B5345"]],
        "orden": 1,
    },
    "POTENCIALES 2%": {
        "label": "🟠 POTENCIALES 2% (Penetración 2% a < 5%)",
        "short": "POTENCIALES 2% (2% – 4.98%)",
        "color": "#E67E22",       # Naranja / Ámbar intenso
        "color_light": "#F39C12",
        "bg_badge": "#FEF9E7",
        "rango_desc": "Índice de Penetración entre 2.0% y 4.98%",
        "colorscale": [[0.0, "#FCF3CF"], [0.35, "#F5B041"], [0.7, "#E67E22"], [1.0, "#873600"]],
        "orden": 2,
    },
    "INFERIORES A 2%": {
        "label": "🔴 INFERIORES A 2% (Penetración < 2%)",
        "short": "INFERIORES A 2% (< 2%)",
        "color": "#D61C38",       # Rojo Carmesí CCE
        "color_light": "#E74C3C",
        "bg_badge": "#FDEDEC",
        "rango_desc": "Índice de Penetración < 2.0% (0.00% a 1.99%)",
        "colorscale": [[0.0, "#FADBD8"], [0.35, "#EC7063"], [0.7, "#D61C38"], [1.0, "#641E16"]],
        "orden": 3,
    },
}

MAP_STYLES = {
    "Claro Institucional (Carto Positron)": "carto-positron",
    "Oscuro Ejecutivo (Carto Darkmatter)": "carto-darkmatter",
    "Mapa Vial Detallado (OpenStreetMap)": "open-street-map",
}

# ── Estilos CSS ───────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #174073 0%, #3E546C 100%); }
[data-testid="stSidebar"] * { color: #fff !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stRadio label {
    color: #FFC000 !important;
    font-size: 0.80rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}
.hero-2027 {
    background: linear-gradient(135deg, #174073 0%, #1F618D 55%, #1E8449 100%);
    color: white;
    padding: 1.45rem 1.8rem;
    border-radius: 16px;
    margin-bottom: 1.2rem;
    box-shadow: 0 6px 24px rgba(23,64,115,0.18);
}
.hero-2027 h1 { color: white !important; font-size: 1.65rem; margin: 0 0 0.35rem 0; font-weight: 700; }
.hero-2027 p { color: #EBF5FB; margin: 0; font-size: 0.92rem; line-height: 1.45; }
.kpi-box {
    background: white;
    border-radius: 14px;
    padding: 1.1rem 1.3rem;
    box-shadow: 0 4px 16px rgba(23,64,115,0.09);
    border-left: 6px solid #174073;
    height: 100%;
}
.kpi-box .title { font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: #566573; letter-spacing: 0.04em; }
.kpi-box .value { font-size: 1.75rem; font-weight: 700; color: #174073; margin: 0.2rem 0; }
.kpi-box .sub { font-size: 0.78rem; color: #5D6D7E; }
.section-header {
    font-size: 1.15rem;
    font-weight: 700;
    color: #174073;
    border-bottom: 3px solid #D61C38;
    padding-bottom: 0.4rem;
    margin: 1.5rem 0 1rem 0;
}
.sim-card {
    background: #F8FAFC;
    border: 1px solid #D6DBDF;
    border-radius: 14px;
    padding: 1.1rem 1.4rem;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

# ── Carga de datos y GeoJSON ──────────────────────────────────────────────
df_raw = get_data_2027()
geojson_mpio = load_geojson_municipios()
geojson_depto = load_geojson_departamentos()

if df_raw.empty:
    st.error("No se encontró la base de despliegue 2027–2028 (`emae_despliegue_2027_2028.parquet`).")
    st.stop()

# ── Barra Lateral de Filtros ──────────────────────────────────────────────
with st.sidebar:
    logo_path = BASE_DIR / "assets" / "escudo.png"
    if logo_path.exists():
        st.image(str(logo_path), use_container_width=True)

    st.markdown("## 🚀 DESPLIEGUE 2027–2028")
    st.markdown("**Potenciales Entidades a Obligar**")
    st.caption("Segmentación por Índice de Penetración MinTIC")
    st.markdown("---")

    hojas_disp = ["POTENCIALES 5%", "POTENCIALES 2%", "INFERIORES A 2%"]
    sel_hojas = st.multiselect(
        "Libros / Hojas del Excel",
        options=hojas_disp,
        default=hojas_disp,
        format_func=lambda h: SHEET_META[h]["label"],
    )

    deptos_disp = sorted(df_raw["DEPARTAMENTO"].dropna().unique().tolist())
    sel_deptos = st.multiselect("Departamento", options=deptos_disp, default=[])

    cgn_order = ["Especial", "Primera", "Segunda", "Tercera", "Cuarta", "Quinta", "Sexta"]
    cgn_disp = [c for c in cgn_order if c in df_raw["CATEGORIA_CGN"].unique()]
    sel_cgn = st.multiselect("Categoría CGN", options=cgn_disp, default=[])

    nat_disp = sorted(df_raw["NATURALEZA_INSTITUCIONAL"].dropna().unique().tolist())
    sel_nat = st.multiselect("Naturaleza Institucional", options=nat_disp, default=[])

    sel_pub = st.radio(
        "¿Publica actualmente en SECOP II?",
        options=["Todas", "Sí", "No"],
        horizontal=True,
    )

    st.markdown("---")
    st.caption(f"📊 Universo Total: **{len(df_raw):,}** entidades en **{df_raw['CODIGO_DIVIPOLA_MAPA'].nunique():,}** municipios DIVIPOLA")

# Aplicar filtros laterales
df = df_raw.copy()
if sel_hojas:
    df = df[df["HOJA_ORIGEN"].isin(sel_hojas)]
else:
    df = df.iloc[0:0]

if sel_deptos:
    df = df[df["DEPARTAMENTO"].isin(sel_deptos)]
if sel_cgn:
    df = df[df["CATEGORIA_CGN"].isin(sel_cgn)]
if sel_nat:
    df = df[df["NATURALEZA_INSTITUCIONAL"].isin(sel_nat)]
if sel_pub != "Todas":
    df = df[df["PUBLICA_EN_SECOP2"] == sel_pub]

# ── Encabezado Hero ───────────────────────────────────────────────────────
st.markdown("""
<div class="hero-2027">
    <h1>🚀 Despliegue SECOP II (2027–2028) – Potenciales Entidades a Obligar</h1>
    <p>
        Georreferenciación nacional por <b>Código DIVIPOLA</b> y modelado de incorporación gradual de las 
        <b>2.011 entidades territoriales</b> según el <b>Índice de Penetración de Internet Fijo MinTIC</b> 
        estructurado en los 3 libros oficiales: <b>POTENCIALES 5%</b> (≥ 5%), <b>POTENCIALES 2%</b> (2% a &lt; 5%) 
        e <b>INFERIORES A 2%</b> (&lt; 2%).
    </p>
</div>
""", unsafe_allow_html=True)

# ── Tarjetas KPI por Libro / Hoja ─────────────────────────────────────────
df_5 = df[df["HOJA_ORIGEN"] == "POTENCIALES 5%"]
df_2 = df[df["HOJA_ORIGEN"] == "POTENCIALES 2%"]
df_inf2 = df[df["HOJA_ORIGEN"] == "INFERIORES A 2%"]

total_ent = len(df)
total_mpios = df["CODIGO_DIVIPOLA_MAPA"].nunique()
total_proc = int(df["TOTAL_PROCESOS_S1"].sum())
total_val = float(df["VALOR_TOTAL_CUANTIA_S1"].sum())

k0, k1, k2, k3 = st.columns(4)
with k0:
    st.markdown(f"""
    <div class="kpi-box" style="border-left-color:#174073;">
        <div class="title">🏛️ Total Universo Filtrado</div>
        <div class="value">{total_ent:,} <span style="font-size:0.95rem;font-weight:500;">entidades</span></div>
        <div class="sub">📍 <b>{total_mpios:,}</b> municipios DIVIPOLA | 📄 <b>{total_proc:,}</b> proc.<br>💰 Cuantía S1: <b>{fmt_billones(total_val, short=True)}</b></div>
    </div>
    """, unsafe_allow_html=True)

with k1:
    pct_5 = (len(df_5) / total_ent * 100) if total_ent > 0 else 0
    st.markdown(f"""
    <div class="kpi-box" style="border-left-color:#1E8449;background:#F9FEFB;">
        <div class="title" style="color:#1E8449;">🟢 Hoja 1: POTENCIALES 5%</div>
        <div class="value" style="color:#1E8449;">{len(df_5):,} <span style="font-size:0.95rem;">({pct_5:.1f}%)</span></div>
        <div class="sub">📡 Penetración <b>≥ 5.0%</b> (5.02% – 36.71%)<br>📍 <b>{df_5['CODIGO_DIVIPOLA_MAPA'].nunique():,}</b> municipios | 📄 <b>{int(df_5['TOTAL_PROCESOS_S1'].sum()):,}</b> proc.</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    pct_2 = (len(df_2) / total_ent * 100) if total_ent > 0 else 0
    st.markdown(f"""
    <div class="kpi-box" style="border-left-color:#E67E22;background:#FFFCF5;">
        <div class="title" style="color:#B95804;">🟠 Hoja 2: POTENCIALES 2%</div>
        <div class="value" style="color:#D35400;">{len(df_2):,} <span style="font-size:0.95rem;">({pct_2:.1f}%)</span></div>
        <div class="sub">📡 Penetración <b>2.0% a &lt; 5.0%</b> (2.00% – 4.98%)<br>📍 <b>{df_2['CODIGO_DIVIPOLA_MAPA'].nunique():,}</b> municipios | 📄 <b>{int(df_2['TOTAL_PROCESOS_S1'].sum()):,}</b> proc.</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    pct_i2 = (len(df_inf2) / total_ent * 100) if total_ent > 0 else 0
    st.markdown(f"""
    <div class="kpi-box" style="border-left-color:#D61C38;background:#FFF9F9;">
        <div class="title" style="color:#D61C38;">🔴 Hoja 3: INFERIORES A 2%</div>
        <div class="value" style="color:#C0392B;">{len(df_inf2):,} <span style="font-size:0.95rem;">({pct_i2:.1f}%)</span></div>
        <div class="sub">📡 Penetración <b>&lt; 2.0%</b> (0.00% – 1.99%)<br>📍 <b>{df_inf2['CODIGO_DIVIPOLA_MAPA'].nunique():,}</b> municipios | 📄 <b>{int(df_inf2['TOTAL_PROCESOS_S1'].sum()):,}</b> proc.</div>
    </div>
    """, unsafe_allow_html=True)


# ── Helpers de agregación geográfica por Código DIVIPOLA ──────────────────
def agg_by_divipola(data: pd.DataFrame) -> pd.DataFrame:
    if data.empty:
        return pd.DataFrame()
    pub_s2 = (
        data[data["PUBLICA_EN_SECOP2"] == "Sí"]
        .groupby("CODIGO_DIVIPOLA_MAPA", observed=True)["NOMBRE_ENTIDAD"]
        .nunique()
        .rename("ent_s2")
    )
    agg = (
        data.groupby(["CODIGO_DIVIPOLA_MAPA", "CODIGO_DIVIPOLA", "DEPARTAMENTO", "MUNICIPIO", "HOJA_ORIGEN"], observed=True)
        .agg(
            entidades=("NOMBRE_ENTIDAD", "count"),
            procesos=("TOTAL_PROCESOS_S1", "sum"),
            valor_cop=("VALOR_TOTAL_CUANTIA_S1", "sum"),
            penetracion_pct=("PENETRACION_PCT", "mean"),
            categoria_cgn=("CATEGORIA_CGN", "first"),
            lat=("LATITUD", "first"),
            lon=("LONGITUD", "first"),
            lista_entidades=("NOMBRE_ENTIDAD", lambda s: " • ".join(list(s)[:4]) + (f" (+{len(s)-4} más)" if len(s) > 4 else "")),
        )
        .reset_index()
    )
    agg = agg.merge(pub_s2, on="CODIGO_DIVIPOLA_MAPA", how="left")
    agg["ent_s2"] = agg["ent_s2"].fillna(0).astype(int)
    agg["pct_s2"] = np.where(agg["entidades"] > 0, agg["ent_s2"] / agg["entidades"] * 100.0, 0.0)
    agg["valor_mm"] = agg["valor_cop"] / 1e9
    return agg


def build_multilayer_colombia_map(
    df_in: pd.DataFrame,
    geojson_mpio: dict,
    modo_visual: str,
    estilo_mapa: str,
    metrica_tam: str,
    df_contexto_gris: pd.DataFrame = None,
) -> go.Figure:
    """
    Construye el Mapa de Colombia con Código DIVIPOLA coloreando las entidades de cada hoja
    con su color distintivo (Verde: POTENCIALES 5%, Naranja: POTENCIALES 2%, Rojo: INFERIORES A 2%).
    Soporta pintar una sola hoja, combinación de hojas, y opcionalmente el resto en gris de referencia.
    """
    agg = agg_by_divipola(df_in)
    if agg.empty and (df_contexto_gris is None or df_contexto_gris.empty):
        return go.Figure()

    base_ref = agg if not agg.empty else agg_by_divipola(df_contexto_gris)
    n_deptos = base_ref["DEPARTAMENTO"].nunique()
    if n_deptos == 1:
        center = dict(lat=float(base_ref["lat"].mean()), lon=float(base_ref["lon"].mean()))
        zoom = 6.8
    elif n_deptos <= 4:
        center = dict(lat=float(base_ref["lat"].mean()), lon=float(base_ref["lon"].mean()))
        zoom = 5.7
    else:
        center = dict(lat=4.5709, lon=-74.2973)
        zoom = 4.75

    fig = go.Figure()

    # 0. Si el usuario activó ver las hojas no seleccionadas en gris de referencia
    if df_contexto_gris is not None and not df_contexto_gris.empty:
        agg_gris = agg_by_divipola(df_contexto_gris)
        if not agg_gris.empty:
            if modo_visual in ("poligonos_y_burbujas", "solo_poligonos") and geojson_mpio:
                codes_g = set(agg_gris["CODIGO_DIVIPOLA_MAPA"].unique())
                sub_geo_g = {
                    "type": "FeatureCollection",
                    "features": [f for f in geojson_mpio.get("features", []) if f.get("id") in codes_g],
                }
                fig.add_trace(go.Choroplethmap(
                    geojson=sub_geo_g,
                    locations=agg_gris["CODIGO_DIVIPOLA_MAPA"],
                    featureidkey="id",
                    z=np.ones(len(agg_gris)),
                    colorscale=[[0, "#D5D8DC"], [1, "#D5D8DC"]],
                    showscale=False,
                    name="⚪ Otras Hojas (No seleccionadas)",
                    marker_opacity=0.45,
                    marker_line_width=0.4,
                    marker_line_color="rgba(180,180,180,0.6)",
                    customdata=np.stack([
                        agg_gris["MUNICIPIO"],
                        agg_gris["DEPARTAMENTO"],
                        agg_gris["CODIGO_DIVIPOLA"],
                        agg_gris["HOJA_ORIGEN"],
                        agg_gris["penetracion_pct"],
                        agg_gris["entidades"],
                    ], axis=-1),
                    hovertemplate=(
                        "<b>⚪ (No seleccionada) %{customdata[0]} (%{customdata[1]})</b><br>"
                        "DIVIPOLA: %{customdata[2]} | Hoja: <b>%{customdata[3]}</b><br>"
                        "Penetración: %{customdata[4]:.2f}% | Entidades: %{customdata[5]}<extra></extra>"
                    ),
                ))
            else:
                fig.add_trace(go.Scattermap(
                    lat=agg_gris["lat"],
                    lon=agg_gris["lon"],
                    mode="markers",
                    name="⚪ Otras Hojas (No seleccionadas)",
                    marker=dict(size=6, color="#BDC3C7", opacity=0.50),
                    customdata=np.stack([
                        agg_gris["MUNICIPIO"],
                        agg_gris["DEPARTAMENTO"],
                        agg_gris["CODIGO_DIVIPOLA"],
                        agg_gris["HOJA_ORIGEN"],
                        agg_gris["penetracion_pct"],
                        agg_gris["entidades"],
                    ], axis=-1),
                    hovertemplate=(
                        "<b>⚪ (No seleccionada) %{customdata[0]} (%{customdata[1]})</b><br>"
                        "DIVIPOLA: %{customdata[2]} | Hoja: <b>%{customdata[3]}</b><br>"
                        "Penetración: %{customdata[4]:.2f}% | Entidades: %{customdata[5]}<extra></extra>"
                    ),
                ))

    if agg.empty:
        fig.update_layout(
            map=dict(style=estilo_mapa, center=center, zoom=zoom),
            margin=dict(l=0, r=0, t=10, b=0),
            height=640,
        )
        return fig

    # Filtrar GeoJSON para los municipios activos
    valid_codes = set(agg["CODIGO_DIVIPOLA_MAPA"].unique())
    sub_geo = {
        "type": "FeatureCollection",
        "features": [f for f in geojson_mpio.get("features", []) if f.get("id") in valid_codes],
    } if geojson_mpio else {"type": "FeatureCollection", "features": []}

    hojas_presentes = [h for h in ["POTENCIALES 5%", "POTENCIALES 2%", "INFERIORES A 2%"] if h in agg["HOJA_ORIGEN"].unique()]
    una_sola_hoja = len(hojas_presentes) == 1

    # 1. Si el modo incluye Polígonos Coropléticos DIVIPOLA por Hoja
    if modo_visual in ("poligonos_y_burbujas", "solo_poligonos") and sub_geo["features"]:
        for hoja in hojas_presentes:
            sub_df = agg[agg["HOJA_ORIGEN"] == hoja]
            if sub_df.empty:
                continue
            meta = SHEET_META[hoja]
            customdata = np.stack([
                sub_df["MUNICIPIO"],
                sub_df["DEPARTAMENTO"],
                sub_df["CODIGO_DIVIPOLA"],
                sub_df["HOJA_ORIGEN"],
                sub_df["penetracion_pct"],
                sub_df["entidades"],
                sub_df["procesos"],
                sub_df["valor_mm"],
                sub_df["categoria_cgn"],
                sub_df["lista_entidades"],
            ], axis=-1)

            fig.add_trace(go.Choroplethmap(
                geojson=sub_geo,
                locations=sub_df["CODIGO_DIVIPOLA_MAPA"],
                featureidkey="id",
                z=sub_df["entidades"],
                colorscale=meta["colorscale"],
                showscale=una_sola_hoja,
                colorbar=dict(
                    title=dict(text="Entidades", font=dict(size=12, color=meta["color"])),
                    thickness=14,
                    len=0.65,
                ) if una_sola_hoja else None,
                name=meta["short"],
                marker_opacity=0.84,
                marker_line_width=0.75,
                marker_line_color="rgba(255,255,255,0.80)",
                customdata=customdata,
                hovertemplate=(
                    "<b>📍 %{customdata[0]} (%{customdata[1]})</b><br>"
                    "Código DIVIPOLA: <b>%{customdata[2]}</b> | Categoría CGN: <b>%{customdata[8]}</b><br>"
                    "Libro / Hoja: <b>%{customdata[3]}</b><br>"
                    "──────────────────────────────<br>"
                    "• <b>Índice Penetración MinTIC:</b> %{customdata[4]:.2f}%<br>"
                    "• <b>Entidades a Obligar:</b> %{customdata[5]:,}<br>"
                    "• <b>Procesos SECOP I:</b> %{customdata[6]:,}<br>"
                    "• <b>Cuantía S1:</b> $%{customdata[7]:,.1f} MM COP<br>"
                    "• <b>Entidades:</b> %{customdata[9]}<extra></extra>"
                ),
            ))

    # 2. Si el modo es Mapa de Calor de Densidad + Puntos por Hoja
    if modo_visual == "calor_y_puntos":
        col_weight = {
            "entidades": "entidades",
            "procesos": "procesos",
            "valor": "valor_mm",
            "penetracion": "penetracion_pct",
        }.get(metrica_tam, "entidades")

        # Si hay una sola hoja elegida, usar la escala de calor del color de esa hoja
        if una_sola_hoja:
            h_unica = hojas_presentes[0]
            heat_scale = SHEET_META[h_unica]["colorscale"]
        else:
            heat_scale = [
                [0.0, "rgba(255,255,255,0)"],
                [0.25, "rgba(241,196,15,0.45)"],
                [0.6, "rgba(230,126,34,0.70)"],
                [1.0, "rgba(214,28,56,0.92)"],
            ]

        fig.add_trace(go.Densitymap(
            lat=agg["lat"],
            lon=agg["lon"],
            z=agg[col_weight],
            radius=22 if una_sola_hoja else 20,
            colorscale=heat_scale,
            showscale=False,
            hoverinfo="skip",
            name="Halo de Calor",
        ))

    # 3. Burbujas / Puntos Georreferenciados coloreados por Hoja
    if modo_visual in ("poligonos_y_burbujas", "calor_y_puntos", "solo_burbujas"):
        col_sz = {
            "entidades": "entidades",
            "procesos": "procesos",
            "valor": "valor_mm",
            "penetracion": "penetracion_pct",
        }.get(metrica_tam, "entidades")
        max_v = max(float(agg[col_sz].max()), 1.0)

        for hoja in ["POTENCIALES 5%", "POTENCIALES 2%", "INFERIORES A 2%"]:
            sub_df = agg[agg["HOJA_ORIGEN"] == hoja]
            if sub_df.empty:
                continue
            meta = SHEET_META[hoja]
            sizes = 8 + 20 * np.sqrt(np.clip(sub_df[col_sz], 0, None) / max_v)
            customdata = np.stack([
                sub_df["MUNICIPIO"],
                sub_df["DEPARTAMENTO"],
                sub_df["CODIGO_DIVIPOLA"],
                sub_df["HOJA_ORIGEN"],
                sub_df["penetracion_pct"],
                sub_df["entidades"],
                sub_df["procesos"],
                sub_df["valor_mm"],
                sub_df["categoria_cgn"],
                sub_df["lista_entidades"],
            ], axis=-1)

            fig.add_trace(go.Scattermap(
                lat=sub_df["lat"],
                lon=sub_df["lon"],
                mode="markers",
                name=meta["label"],
                marker=dict(
                    size=sizes,
                    color=meta["color"],
                    opacity=0.88 if modo_visual != "poligonos_y_burbujas" else 0.92,
                ),
                customdata=customdata,
                hovertemplate=(
                    "<b>📍 %{customdata[0]} (%{customdata[1]})</b><br>"
                    "Código DIVIPOLA: <b>%{customdata[2]}</b> | Categoría CGN: <b>%{customdata[8]}</b><br>"
                    "Libro / Hoja: <b>%{customdata[3]}</b><br>"
                    "──────────────────────────────<br>"
                    "• <b>Índice Penetración MinTIC:</b> %{customdata[4]:.2f}%<br>"
                    "• <b>Entidades a Obligar:</b> %{customdata[5]:,}<br>"
                    "• <b>Procesos SECOP I:</b> %{customdata[6]:,}<br>"
                    "• <b>Cuantía S1:</b> $%{customdata[7]:,.1f} MM COP<br>"
                    "• <b>Entidades:</b> %{customdata[9]}<extra></extra>"
                ),
            ))

    # 4. Modo Coroplético Continuo por Índice de Penetración MinTIC (%)
    if modo_visual == "coropletico_penetracion" and sub_geo["features"]:
        customdata = np.stack([
            agg["MUNICIPIO"],
            agg["DEPARTAMENTO"],
            agg["CODIGO_DIVIPOLA"],
            agg["HOJA_ORIGEN"],
            agg["penetracion_pct"],
            agg["entidades"],
            agg["procesos"],
            agg["valor_mm"],
            agg["categoria_cgn"],
            agg["lista_entidades"],
        ], axis=-1)

        fig.add_trace(go.Choroplethmap(
            geojson=sub_geo,
            locations=agg["CODIGO_DIVIPOLA_MAPA"],
            featureidkey="id",
            z=agg["penetracion_pct"],
            colorscale=[
                [0.0, "#D61C38"],    # < 2% Rojo
                [0.06, "#E67E22"],   # ~2% Naranja
                [0.15, "#F1C40F"],   # ~5% Amarillo
                [0.35, "#2ECC71"],   # ~12% Verde claro
                [1.0, "#0B5345"],    # >30% Verde oscuro
            ],
            marker_opacity=0.86,
            marker_line_width=0.6,
            marker_line_color="rgba(255,255,255,0.7)",
            colorbar=dict(
                title=dict(text="Penetración (%)", font=dict(size=12, color="#174073")),
                thickness=15,
                len=0.72,
                ticksuffix="%",
            ),
            customdata=customdata,
            hovertemplate=(
                "<b>📍 %{customdata[0]} (%{customdata[1]})</b><br>"
                "Código DIVIPOLA: <b>%{customdata[2]}</b> | Libro: <b>%{customdata[3]}</b><br>"
                "──────────────────────────────<br>"
                "• <b>Índice Penetración MinTIC:</b> %{customdata[4]:.2f}%<br>"
                "• <b>Entidades a Obligar:</b> %{customdata[5]:,}<br>"
                "• <b>Procesos SECOP I:</b> %{customdata[6]:,}<br>"
                "• <b>Entidades:</b> %{customdata[9]}<extra></extra>"
            ),
        ))

    fig.update_layout(
        map=dict(
            style=estilo_mapa,
            center=center,
            zoom=zoom,
        ),
        margin=dict(l=0, r=0, t=10, b=0),
        height=640,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=0.02,
            xanchor="left",
            x=0.02,
            bgcolor="rgba(255,255,255,0.92)",
            bordercolor="#174073",
            borderwidth=1,
            font=dict(size=12, color="#174073"),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════
# SECCIÓN 1: MAPA PRINCIPAL MULTICAPA DE COLOMBIA (CÓDIGO DIVIPOLA)
# ══════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="section-header">🗺️ Mapa de Calor de Colombia por Código DIVIPOLA – Selección por Hoja</div>',
    unsafe_allow_html=True,
)

# ── Selector directo de las 3 hojas ───────────────────────────────────────
st.markdown("**Seleccione la(s) hoja(s) a dibujar en el mapa (si elige dos o más se superponen):**")
chk_col1, chk_col2, chk_col3 = st.columns(3)
with chk_col1:
    chk_h1 = st.checkbox("🟢 Hoja 1: POTENCIALES 5% (Penetración ≥ 5%)", value=True, key="chk_h1")
with chk_col2:
    chk_h2 = st.checkbox("🟠 Hoja 2: POTENCIALES 2% (Penetración 2% a < 5%)", value=True, key="chk_h2")
with chk_col3:
    chk_h3 = st.checkbox("🔴 Hoja 3: INFERIORES A 2% (Penetración < 2%)", value=True, key="chk_h3")

hojas_a_pintar = []
if chk_h1:
    hojas_a_pintar.append("POTENCIALES 5%")
if chk_h2:
    hojas_a_pintar.append("POTENCIALES 2%")
if chk_h3:
    hojas_a_pintar.append("INFERIORES A 2%")

df_mapa_activo = df[df["HOJA_ORIGEN"].isin(hojas_a_pintar)]
df_mapa_gris = None

ctrl1, ctrl2, ctrl3 = st.columns([1.6, 1.2, 1.2])
with ctrl1:
    modo_mapa = st.selectbox(
        "🎨 Modo de Visualización del Mapa DIVIPOLA:",
        options=[
            "poligonos_y_burbujas",
            "calor_y_puntos",
            "solo_poligonos",
            "solo_burbujas",
            "coropletico_penetracion",
        ],
        format_func=lambda m: {
            "poligonos_y_burbujas": "🗺️ Polígonos Municipales DIVIPOLA + Burbujas por Color de Hoja (Recomendado)",
            "calor_y_puntos": "🔥 Mapa de Calor Térmico (Heatmap) + Puntos por Color de Hoja",
            "solo_poligonos": "🧩 Solo Polígonos Municipales GeoJSON Coloreados por Hoja",
            "solo_burbujas": "🔵 Burbujas Georreferenciadas por Código DIVIPOLA y Hoja",
            "coropletico_penetracion": "📡 Gradiente Continuo de Índice de Penetración MinTIC (%)",
        }[m],
        index=0,
    )

with ctrl2:
    metrica_tam = st.selectbox(
        "📏 Escalar intensidad / tamaño por:",
        options=["entidades", "procesos", "valor", "penetracion"],
        format_func=lambda x: {
            "entidades": "🏛️ N° de Entidades a Obligar",
            "procesos": "📄 Total Procesos SECOP I",
            "valor": "💰 Cuantía Total ($MM COP)",
            "penetracion": "📡 Índice de Penetración MinTIC (%)",
        }[x],
    )

with ctrl3:
    estilo_label = st.selectbox(
        "🌐 Estilo del Mapa Base:",
        options=list(MAP_STYLES.keys()),
        index=0,
    )
    estilo_mapa = MAP_STYLES[estilo_label]

fig_main_map = build_multilayer_colombia_map(
    df_in=df_mapa_activo,
    geojson_mpio=geojson_mpio,
    modo_visual=modo_mapa,
    estilo_mapa=estilo_mapa,
    metrica_tam=metrica_tam,
    df_contexto_gris=df_mapa_gris,
)
st.plotly_chart(fig_main_map, use_container_width=True, key="map_2027_main")

st.caption(
    "💡 **Guía interactiva del mapa:** Use el selector superior para **elegir si desea pintar la Hoja 1 (`POTENCIALES 5%`), "
    "la Hoja 2 (`POTENCIALES 2%`), la Hoja 3 (`INFERIORES A 2%`) o combinaciones entre ellas**. "
    "Cuando selecciona una sola hoja, el mapa aplica su escala de calor exclusiva y despliega la barra de intensidad."
)


# ══════════════════════════════════════════════════════════════════════════
# SECCIÓN 2: TRÍPTICO DE MAPAS DE CALOR INDIVIDUALES POR LIBRO / HOJA
# ══════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="section-header">🔥 Los 3 Libros en Mapas de Calor Individuales (Comparativa Geográfica por Hoja)</div>',
    unsafe_allow_html=True,
)
st.markdown(
    "Visualización simultánea de la huella territorial de cada hoja del archivo **`BASE DE DATOS POTENCIALES ENTIDADES A OBLIGAR`**, "
    "mostrando cómo varía la concentración geográfica según el tramo del índice de penetración:"
)

tipo_triptico = st.radio(
    "Tipo de representación en los 3 mapas:",
    options=["densidad_y_puntos", "coropletico_divipola"],
    format_func=lambda x: (
        "🔥 Mapa de Calor Térmico + Puntos DIVIPOLA (Color propio por hoja)"
        if x == "densidad_y_puntos"
        else "🧩 Polígonos Municipales Coropléticos (Código DIVIPOLA)"
    ),
    horizontal=True,
)

col_m1, col_m2, col_m3 = st.columns(3)

for col_ui, hoja_key in zip([col_m1, col_m2, col_m3], ["POTENCIALES 5%", "POTENCIALES 2%", "INFERIORES A 2%"]):
    meta = SHEET_META[hoja_key]
    df_h = df[df["HOJA_ORIGEN"] == hoja_key]
    agg_h = agg_by_divipola(df_h)

    with col_ui:
        st.markdown(
            f"<div style='background:{meta['bg_badge']};border-top:4px solid {meta['color']};padding:0.65rem 0.9rem;border-radius:10px;margin-bottom:0.4rem;'>"
            f"<b style='color:{meta['color']};font-size:0.95rem;'>{meta['label']}</b><br>"
            f"<span style='font-size:0.80rem;color:#34495E;'><b>{len(df_h):,}</b> entidades en <b>{agg_h['CODIGO_DIVIPOLA_MAPA'].nunique() if not agg_h.empty else 0:,}</b> municipios DIVIPOLA</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

        fig_h = go.Figure()
        if not agg_h.empty:
            if tipo_triptico == "coropletico_divipola" and geojson_mpio:
                codes_h = set(agg_h["CODIGO_DIVIPOLA_MAPA"].unique())
                sub_geo_h = {
                    "type": "FeatureCollection",
                    "features": [f for f in geojson_mpio.get("features", []) if f.get("id") in codes_h],
                }
                fig_h.add_trace(go.Choroplethmap(
                    geojson=sub_geo_h,
                    locations=agg_h["CODIGO_DIVIPOLA_MAPA"],
                    featureidkey="id",
                    z=agg_h["entidades"],
                    colorscale=meta["colorscale"],
                    showscale=False,
                    marker_opacity=0.88,
                    marker_line_width=0.5,
                    marker_line_color="white",
                    customdata=np.stack([
                        agg_h["MUNICIPIO"],
                        agg_h["DEPARTAMENTO"],
                        agg_h["CODIGO_DIVIPOLA"],
                        agg_h["penetracion_pct"],
                        agg_h["entidades"],
                    ], axis=-1),
                    hovertemplate=(
                        "<b>📍 %{customdata[0]} (%{customdata[1]})</b><br>"
                        "DIVIPOLA: <b>%{customdata[2]}</b><br>"
                        "Penetración: <b>%{customdata[3]:.2f}%</b><br>"
                        "Entidades: <b>%{customdata[4]:,}</b><extra></extra>"
                    ),
                ))
            else:
                fig_h.add_trace(go.Densitymap(
                    lat=agg_h["lat"],
                    lon=agg_h["lon"],
                    z=agg_h["entidades"],
                    radius=18,
                    colorscale=meta["colorscale"],
                    showscale=False,
                    hoverinfo="skip",
                ))
                fig_h.add_trace(go.Scattermap(
                    lat=agg_h["lat"],
                    lon=agg_h["lon"],
                    mode="markers",
                    marker=dict(
                        size=7 + 10 * np.sqrt(agg_h["entidades"] / max(agg_h["entidades"].max(), 1)),
                        color=meta["color"],
                        opacity=0.88,
                    ),
                    customdata=np.stack([
                        agg_h["MUNICIPIO"],
                        agg_h["DEPARTAMENTO"],
                        agg_h["CODIGO_DIVIPOLA"],
                        agg_h["penetracion_pct"],
                        agg_h["entidades"],
                        agg_h["lista_entidades"],
                    ], axis=-1),
                    hovertemplate=(
                        "<b>📍 %{customdata[0]} (%{customdata[1]})</b><br>"
                        "DIVIPOLA: <b>%{customdata[2]}</b><br>"
                        "Penetración MinTIC: <b>%{customdata[3]:.2f}%</b><br>"
                        "Entidades: <b>%{customdata[4]:,}</b><br>"
                        "%{customdata[5]}<extra></extra>"
                    ),
                    showlegend=False,
                ))

        fig_h.update_layout(
            map=dict(style=estilo_mapa, center=dict(lat=4.5709, lon=-74.2973), zoom=4.15),
            margin=dict(l=0, r=0, t=0, b=0),
            height=410,
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_h, use_container_width=True, key=f"map_trip_{hoja_key}")


# ══════════════════════════════════════════════════════════════════════════
# SECCIÓN 3: SIMULADOR DE INCORPORACIÓN PROGRESIVA SEGÚN ÍNDICE DE PENETRACIÓN
# ══════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="section-header">🎚️ Simulador de Incorporación de Entidades según Índice de Penetración MinTIC</div>',
    unsafe_allow_html=True,
)
st.markdown(
    "Evalúe en tiempo real cuántas entidades, municipios, procesos y recursos se **incorporan a la obligatoriedad SECOP II** "
    "al definir un umbral determinado del **Índice de Penetración de Internet Fijo**:"
)

sim_c1, sim_c2 = st.columns([1.4, 1.6])
with sim_c1:
    preset_umbral = st.radio(
        "Seleccione un corte estratégico o use el control deslizante:",
        options=[
            "Tramo 1: Umbral ≥ 5.0% (Incorpora Hoja POTENCIALES 5%)",
            "Tramo 1 + 2: Umbral ≥ 2.0% (Incorpora POTENCIALES 5% + POTENCIALES 2%)",
            "Cobertura Total: Umbral ≥ 0.0% (Incorpora las 3 Hojas)",
            "Umbral Personalizado (Usar deslizador)",
        ],
        index=1,
    )

with sim_c2:
    if preset_umbral.startswith("Tramo 1:"):
        umbral_pct = 5.0
        st.info("📌 **Umbral fijado en ≥ 5.0%**: Se incorporan todas las entidades del libro `POTENCIALES 5%`.")
    elif preset_umbral.startswith("Tramo 1 + 2:"):
        umbral_pct = 2.0
        st.info("📌 **Umbral fijado en ≥ 2.0%**: Se incorporan acumuladamente los libros `POTENCIALES 5%` y `POTENCIALES 2%`.")
    elif preset_umbral.startswith("Cobertura Total"):
        umbral_pct = 0.0
        st.info("📌 **Umbral fijado en ≥ 0.0%**: Incorporación del 100% de las entidades de las 3 hojas.")
    else:
        umbral_pct = st.slider(
            "📡 Ajuste el Índice Mínimo de Penetración de Internet (%) para incorporar:",
            min_value=0.0,
            max_value=30.0,
            value=2.0,
            step=0.25,
            format="%.2f%%",
        )

# Calcular incorporación según umbral_pct
df_inc = df[df["PENETRACION_PCT"] >= umbral_pct]
df_pend = df[df["PENETRACION_PCT"] < umbral_pct]

n_inc = len(df_inc)
n_pend = len(df_pend)
pct_inc = (n_inc / len(df) * 100.0) if len(df) > 0 else 0.0
mpios_inc = df_inc["CODIGO_DIVIPOLA_MAPA"].nunique()
proc_inc = int(df_inc["TOTAL_PROCESOS_S1"].sum())
val_inc = float(df_inc["VALOR_TOTAL_CUANTIA_S1"].sum())

sc1, sc2, sc3, sc4 = st.columns(4)
with sc1:
    st.metric(
        label=f"✅ Entidades Incorporadas (≥ {umbral_pct:.2f}%)",
        value=f"{n_inc:,} entidades",
        delta=f"{pct_inc:.1f}% del universo seleccionado",
    )
with sc2:
    st.metric(
        label="📍 Municipios DIVIPOLA Cubiertos",
        value=f"{mpios_inc:,} municipios",
        delta=f"de {df['CODIGO_DIVIPOLA_MAPA'].nunique():,} totales",
    )
with sc3:
    st.metric(
        label="📄 Procesos SECOP I que Migran",
        value=f"{proc_inc:,} procesos",
        delta=f"{fmt_billones(val_inc, short=True)} en cuantía",
    )
with sc4:
    st.metric(
        label=f"⏳ Entidades bajo el umbral (< {umbral_pct:.2f}%)",
        value=f"{n_pend:,} entidades",
        delta=f"{100-pct_inc:.1f}% en brecha conectividad",
        delta_color="off",
    )

col_sim_map, col_sim_curve = st.columns([1.15, 1.0])

with col_sim_map:
    st.markdown(f"**🗺️ Mapa de Incorporación Territorial con Corte ≥ {umbral_pct:.2f}%**")
    fig_sim = go.Figure()

    if not df_pend.empty:
        agg_p = agg_by_divipola(df_pend)
        fig_sim.add_trace(go.Scattermap(
            lat=agg_p["lat"],
            lon=agg_p["lon"],
            mode="markers",
            name=f"⏳ Pendientes / Brecha (< {umbral_pct:.2f}%): {n_pend:,} ent.",
            marker=dict(size=7, color="#BDC3C7", opacity=0.65),
            customdata=np.stack([
                agg_p["MUNICIPIO"], agg_p["DEPARTAMENTO"], agg_p["CODIGO_DIVIPOLA"],
                agg_p["penetracion_pct"], agg_p["entidades"], agg_p["HOJA_ORIGEN"]
            ], axis=-1),
            hovertemplate=(
                "<b>⏳ PENDIENTE: %{customdata[0]} (%{customdata[1]})</b><br>"
                "DIVIPOLA: %{customdata[2]} | Hoja: %{customdata[5]}<br>"
                "Penetración: <b>%{customdata[3]:.2f}%</b> | Entidades: %{customdata[4]}<extra></extra>"
            ),
        ))

    if not df_inc.empty:
        for hoja in ["POTENCIALES 5%", "POTENCIALES 2%", "INFERIORES A 2%"]:
            sub_i = df_inc[df_inc["HOJA_ORIGEN"] == hoja]
            if sub_i.empty:
                continue
            agg_i = agg_by_divipola(sub_i)
            meta = SHEET_META[hoja]
            fig_sim.add_trace(go.Scattermap(
                lat=agg_i["lat"],
                lon=agg_i["lon"],
                mode="markers",
                name=f"✅ Incorporada – {meta['short']} ({len(sub_i):,})",
                marker=dict(
                    size=8 + 12 * np.sqrt(agg_i["entidades"] / max(agg_i["entidades"].max(), 1)),
                    color=meta["color"],
                    opacity=0.90,
                ),
                customdata=np.stack([
                    agg_i["MUNICIPIO"], agg_i["DEPARTAMENTO"], agg_i["CODIGO_DIVIPOLA"],
                    agg_i["penetracion_pct"], agg_i["entidades"], agg_i["HOJA_ORIGEN"]
                ], axis=-1),
                hovertemplate=(
                    "<b>✅ INCORPORADA: %{customdata[0]} (%{customdata[1]})</b><br>"
                    "DIVIPOLA: %{customdata[2]} | Hoja: %{customdata[5]}<br>"
                    "Penetración: <b>%{customdata[3]:.2f}%</b> | Entidades: %{customdata[4]}<extra></extra>"
                ),
            ))

    fig_sim.update_layout(
        map=dict(style=estilo_mapa, center=dict(lat=4.5709, lon=-74.2973), zoom=4.4),
        margin=dict(l=0, r=0, t=5, b=0),
        height=450,
        legend=dict(
            orientation="h", yanchor="bottom", y=0.01, xanchor="left", x=0.01,
            bgcolor="rgba(255,255,255,0.9)", font=dict(size=10.5)
        ),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_sim, use_container_width=True, key="map_sim_2027")

with col_sim_curve:
    st.markdown("**📈 Curva de Incorporación Acumulada según Índice de Penetración**")
    # Construir curva acumulada de mayor a menor penetración
    df_sorted = df.sort_values("PENETRACION_PCT", ascending=False).reset_index(drop=True)
    df_sorted["ENTIDADES_ACUMULADAS"] = np.arange(1, len(df_sorted) + 1)
    df_sorted["PCT_ACUMULADO"] = df_sorted["ENTIDADES_ACUMULADAS"] / max(len(df_sorted), 1) * 100.0

    fig_curve = go.Figure()
    for hoja in ["POTENCIALES 5%", "POTENCIALES 2%", "INFERIORES A 2%"]:
        sub_c = df_sorted[df_sorted["HOJA_ORIGEN"] == hoja]
        if sub_c.empty:
            continue
        meta = SHEET_META[hoja]
        fig_curve.add_trace(go.Scatter(
            x=sub_c["PENETRACION_PCT"],
            y=sub_c["ENTIDADES_ACUMULADAS"],
            mode="lines+markers",
            name=meta["short"],
            marker=dict(size=5, color=meta["color"]),
            line=dict(width=3, color=meta["color"]),
            customdata=np.stack([
                sub_c["NOMBRE_ENTIDAD"],
                sub_c["MUNICIPIO"],
                sub_c["DEPARTAMENTO"],
                sub_c["PCT_ACUMULADO"],
            ], axis=-1),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "%{customdata[1]} (%{customdata[2]})<br>"
                "Penetración: <b>%{x:.2f}%</b><br>"
                "Entidades acumuladas (≥ este índice): <b>%{y:,}</b> (%{customdata[3]:.1f}%)<extra></extra>"
            ),
        ))

    # Líneas de referencia en 5%, 2% y el umbral actual
    fig_curve.add_vline(
        x=5.0, line_dash="dash", line_color="#1E8449",
        annotation_text="Corte 5% (754 ent.)", annotation_position="top right"
    )
    fig_curve.add_vline(
        x=2.0, line_dash="dash", line_color="#E67E22",
        annotation_text="Corte 2% (1.506 ent.)", annotation_position="top right"
    )
    fig_curve.add_vline(
        x=umbral_pct, line_dash="solid", line_color="#174073", line_width=2,
        annotation_text=f"Umbral activo: {umbral_pct:.2f}% ({n_inc:,} ent.)",
        annotation_position="bottom left",
    )

    fig_curve.update_layout(
        xaxis=dict(
            title="Índice de Penetración de Internet Fijo MinTIC (%)",
            autorange="reversed",  # De mayor penetración (izq) a menor penetración (der)
            ticksuffix="%",
            gridcolor="#EBF0F5",
        ),
        yaxis=dict(
            title="N° Acumulado de Entidades Incorporadas",
            gridcolor="#EBF0F5",
        ),
        height=450,
        margin=dict(l=15, r=15, t=20, b=15),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        plot_bgcolor="white",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_curve, use_container_width=True, key="curve_sim_2027")


# ══════════════════════════════════════════════════════════════════════════
# SECCIÓN 4: DESGLOSE DEPARTAMENTAL E INSTITUCIONAL POR HOJA
# ══════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="section-header">📊 Distribución Departamental e Institucional por Libro / Hoja</div>',
    unsafe_allow_html=True,
)

ch1, ch2 = st.columns([1.25, 1.0])

with ch1:
    st.markdown("**🏛️ Top Departamentos según Entidades a Obligar (Desglosado por Hoja)**")
    dpto_grp = (
        df.groupby(["DEPARTAMENTO", "HOJA_ORIGEN"], observed=True)["NOMBRE_ENTIDAD"]
        .count()
        .reset_index(name="entidades")
    )
    tot_dpto = dpto_grp.groupby("DEPARTAMENTO")["entidades"].sum().nlargest(18).index.tolist()
    dpto_top = dpto_grp[dpto_grp["DEPARTAMENTO"].isin(tot_dpto)].copy()

    fig_dpto = px.bar(
        dpto_top,
        y="DEPARTAMENTO",
        x="entidades",
        color="HOJA_ORIGEN",
        orientation="h",
        color_discrete_map={k: v["color"] for k, v in SHEET_META.items()},
        category_orders={
            "DEPARTAMENTO": tot_dpto,
            "HOJA_ORIGEN": ["POTENCIALES 5%", "POTENCIALES 2%", "INFERIORES A 2%"],
        },
        labels={"entidades": "N° de Entidades", "DEPARTAMENTO": "", "HOJA_ORIGEN": "Hoja"},
        text="entidades",
    )
    fig_dpto.update_traces(textposition="inside", insidetextanchor="middle")
    fig_dpto.update_layout(
        barmode="stack",
        height=460,
        margin=dict(l=10, r=15, t=10, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
        plot_bgcolor="white",
        paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(autorange="reversed"),
    )
    st.plotly_chart(fig_dpto, use_container_width=True, key="bar_dpto_2027")

with ch2:
    st.markdown("**🏢 Naturaleza Institucional por Hoja de Penetración**")
    nat_grp = (
        df.groupby(["NATURALEZA_INSTITUCIONAL", "HOJA_ORIGEN"], observed=True)["NOMBRE_ENTIDAD"]
        .count()
        .reset_index(name="entidades")
    )
    fig_nat = px.bar(
        nat_grp,
        x="entidades",
        y="NATURALEZA_INSTITUCIONAL",
        color="HOJA_ORIGEN",
        orientation="h",
        color_discrete_map={k: v["color"] for k, v in SHEET_META.items()},
        category_orders={"HOJA_ORIGEN": ["POTENCIALES 5%", "POTENCIALES 2%", "INFERIORES A 2%"]},
        labels={"entidades": "N° de Entidades", "NATURALEZA_INSTITUCIONAL": "", "HOJA_ORIGEN": "Hoja"},
        text="entidades",
    )
    fig_nat.update_layout(
        barmode="group",
        height=460,
        margin=dict(l=10, r=15, t=10, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
        plot_bgcolor="white",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_nat, use_container_width=True, key="bar_nat_2027")


# ══════════════════════════════════════════════════════════════════════════
# SECCIÓN 5: DIRECTORIO Y DESCARGA DE LOS 3 LIBROS OFICIALES
# ══════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="section-header">📥 Explorador y Descarga de los 3 Libros Oficiales (2027–2028)</div>',
    unsafe_allow_html=True,
)

col_s, col_dl_xl = st.columns([2.4, 1.2])
with col_s:
    busq_txt = st.text_input(
        "🔎 Buscar entidad por nombre, NIT, municipio, departamento o código DIVIPOLA:",
        value="",
        placeholder="Ej: Villa de Leyva, Pasca, Mutiscua, 15407, Personería, Concejo...",
    )
with col_dl_xl:
    st.write("")
    excel_2027_p = BASE_DIR / "BASE DE DATOS POTENCIALES ENTIDADES A OBLIGAR.xlsx"
    if not excel_2027_p.exists():
        excel_2027_p = BASE_DIR.parent / "BASE DE DATOS POTENCIALES ENTIDADES A OBLIGAR.xlsx"
    if excel_2027_p.exists():
        st.download_button(
            label="⬇️ Descargar Excel Original Completo (.xlsx)",
            data=excel_2027_p.read_bytes(),
            file_name="BASE_DE_DATOS_POTENCIALES_ENTIDADES_A_OBLIGAR_2027_2028.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

df_tbl = df.copy()
if busq_txt.strip():
    q = busq_txt.strip().lower()
    mask_q = pd.Series(False, index=df_tbl.index)
    for c_search in ["NOMBRE_ENTIDAD", "NIT_HOMOLOGADO", "MUNICIPIO", "DEPARTAMENTO", "CODIGO_DIVIPOLA", "NATURALEZA_INSTITUCIONAL"]:
        if c_search in df_tbl.columns:
            mask_q |= df_tbl[c_search].astype(str).str.lower().str.contains(q, na=False)
    df_tbl = df_tbl[mask_q]

t_all, t_h1, t_h2, t_h3 = st.tabs([
    f"📚 Consolidado 3 Hojas ({len(df_tbl):,})",
    f"🟢 POTENCIALES 5% ({len(df_tbl[df_tbl['HOJA_ORIGEN']=='POTENCIALES 5%']):,})",
    f"🟠 POTENCIALES 2% ({len(df_tbl[df_tbl['HOJA_ORIGEN']=='POTENCIALES 2%']):,})",
    f"🔴 INFERIORES A 2% ({len(df_tbl[df_tbl['HOJA_ORIGEN']=='INFERIORES A 2%']):,})",
])


def render_sheet_table(sub: pd.DataFrame, file_tag: str, key_suffix: str):
    if sub.empty:
        st.info("No hay registros que coincidan con los filtros actuales.")
        return
    cols_show = [
        "ITEM", "HOJA_ORIGEN", "DEPARTAMENTO", "MUNICIPIO", "CODIGO_DIVIPOLA",
        "NIT_HOMOLOGADO", "NOMBRE_ENTIDAD", "PENETRACION_PCT", "RANGO_CONECTIVIDAD_MINTIC",
        "PUBLICA_EN_SECOP2", "CATEGORIA_CGN", "NATURALEZA_INSTITUCIONAL",
        "TOTAL_PROCESOS_S1", "VALOR_TOTAL_CUANTIA_S1", "NOMBRE_CUENTA_SECOP2",
    ]
    cols_show = [c for c in cols_show if c in sub.columns]
    vista = sub[cols_show].copy()
    vista["PENETRACION_PCT"] = vista["PENETRACION_PCT"].apply(lambda v: f"{v:.2f}%")
    vista["VALOR_TOTAL_CUANTIA_S1"] = vista["VALOR_TOTAL_CUANTIA_S1"].fillna(0).apply(lambda v: f"$ {v:,.0f}")

    st.dataframe(
        vista,
        use_container_width=True,
        hide_index=True,
        height=420,
        column_config={
            "HOJA_ORIGEN": st.column_config.TextColumn("Libro / Hoja"),
            "CODIGO_DIVIPOLA": st.column_config.TextColumn("DIVIPOLA"),
            "PENETRACION_PCT": st.column_config.TextColumn("Penetración MinTIC"),
            "VALOR_TOTAL_CUANTIA_S1": st.column_config.TextColumn("Cuantía Total S1 (COP)", width="medium"),
            "TOTAL_PROCESOS_S1": st.column_config.NumberColumn("Total Procesos S1", format="%d"),
        },
    )
    st.download_button(
        label=f"⬇️ Descargar {file_tag} en CSV ({len(sub):,} filas)",
        data=to_csv_bytes(sub),
        file_name=f"{file_tag}_2027_2028.csv",
        mime="text/csv",
        key=f"dl_{key_suffix}",
    )


with t_all:
    render_sheet_table(df_tbl, "CONSOLIDADO_DESPLIEGUE_2027_2028", "all")
with t_h1:
    render_sheet_table(df_tbl[df_tbl["HOJA_ORIGEN"] == "POTENCIALES 5%"], "POTENCIALES_5_PCT", "h1")
with t_h2:
    render_sheet_table(df_tbl[df_tbl["HOJA_ORIGEN"] == "POTENCIALES 2%"], "POTENCIALES_2_PCT", "h2")
with t_h3:
    render_sheet_table(df_tbl[df_tbl["HOJA_ORIGEN"] == "INFERIORES A 2%"], "INFERIORES_A_2_PCT", "h3")
