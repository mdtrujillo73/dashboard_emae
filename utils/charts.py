"""
Gráficos reutilizables y Mapas de Calor (Departamental y Municipal) para el Dashboard EMAE 2026.
Paleta institucional Colombia Compra Eficiente (ANCP - CCE).
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from utils.data_loader import ESCENARIO_LABELS, ESCENARIO_COLORS, RUTA_SHORT_LABELS

# ── Paleta institucional CCE ────────────────────────────────────────────────
CCE_AMARILLO    = "#FFC000"
CCE_NARANJA     = "#D98A3C"
CCE_CAFE        = "#9C7238"
CCE_GRIS_OSCURO = "#5A666A"
CCE_GRIS_AZUL   = "#3E546C"
CCE_AZUL        = "#174073"
CCE_MORADO      = "#533965"
CCE_VINO_OSCURO = "#6A2444"
CCE_VINO_CLARO  = "#9E2044"
CCE_ROJO        = "#D61C38"

CCE_GRIS  = CCE_GRIS_OSCURO
CCE_CLARO = "#F5F6F8"
CCE_VERDE = "#27AE60"

COLOR_SCALES = {
    "Institucional CCE (Azul-Naranja-Rojo)": [
        [0.0, "#EBF3FA"],
        [0.25, "#7FB3D5"],
        [0.5, "#174073"],
        [0.75, "#D98A3C"],
        [1.0, "#D61C38"],
    ],
    "Calor Intenso (Amarillo-Naranja-Rojo)": "YlOrRd",
    "Azul Institucional": "Blues",
    "Viridis (Alto Contraste)": "Viridis",
    "Plasma": "Plasma",
}

LAYOUT_DEFAULTS = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, Arial, sans-serif", color="#1A1A2E"),
    margin=dict(l=20, r=20, t=40, b=20),
)


def _label_escenario(s: pd.Series) -> pd.Series:
    return s.map(ESCENARIO_LABELS).fillna(s)


# ── Dona de escenarios 2026 ────────────────────────────────────────────────

def chart_dona_escenarios(df: pd.DataFrame, metrica: str = "procesos") -> go.Figure:
    col = "ESCENARIO_2026"
    grp = df.groupby(col, observed=True)
    if metrica == "entidades":
        counts = grp["NOMBRE_ENTIDAD"].nunique().reset_index(name="valor")
        unidad = "Entidades"
    elif metrica == "valor":
        counts = (grp["VALOR_REAL_CUANTIA"].sum() / 1e12).reset_index(name="valor")
        unidad = "Billones COP"
    else:
        counts = grp["CANTIDAD_PROCESOS"].sum().reset_index(name="valor")
        unidad = "Procesos"

    counts.columns = ["escenario", "valor"]
    counts["label"] = _label_escenario(counts["escenario"])
    counts["color"] = counts["escenario"].map(ESCENARIO_COLORS).fillna(CCE_GRIS)

    hover_fmt = "%{value:,.2f}" if metrica == "valor" else "%{value:,}"
    fig = go.Figure(go.Pie(
        labels=counts["label"],
        values=counts["valor"],
        hole=0.56,
        marker=dict(colors=counts["color"].tolist(), line=dict(color="#fff", width=2)),
        textinfo="percent",
        insidetextorientation="auto",
        hovertemplate=f"<b>%{{label}}</b><br>{unidad}: {hover_fmt}<br>%{{percent}}<extra></extra>",
    ))
    fig.update_layout(
        **LAYOUT_DEFAULTS,
        showlegend=True,
        legend=dict(orientation="h", yanchor="top", y=-0.05, xanchor="center", x=0.5, font=dict(size=11)),
        annotations=[dict(
            text=f"<b>{unidad}</b>",
            x=0.5, y=0.5, font_size=13, showarrow=False,
            font_color=CCE_AZUL, font_family="Inter, Arial, sans-serif",
        )],
        height=370,
    )
    return fig


# ── Barras por escenario y vigencia ───────────────────────────────────────

def chart_barras_escenario_vigencia(df: pd.DataFrame, metrica: str = "procesos") -> go.Figure:
    col_esc = "ESCENARIO_2026"
    grp = df.groupby([col_esc, "VIGENCIA"], observed=True)

    if metrica == "procesos" or metrica == "contratos":
        data = grp["CANTIDAD_PROCESOS"].sum().reset_index(name="valor")
        titulo_y = "N° de Procesos SECOP I"
    elif metrica == "entidades":
        data = grp["NOMBRE_ENTIDAD"].nunique().reset_index(name="valor")
        titulo_y = "Entidades Únicas"
    else:
        data = (grp["VALOR_REAL_CUANTIA"].sum() / 1e12).reset_index(name="valor")
        titulo_y = "Cuantía Real (Billones COP)"

    data["label"] = _label_escenario(data[col_esc])
    data["VIGENCIA"] = data["VIGENCIA"].astype(str)

    fig = px.bar(
        data,
        x="VIGENCIA",
        y="valor",
        color="label",
        color_discrete_map={v: ESCENARIO_COLORS.get(k, CCE_GRIS) for k, v in ESCENARIO_LABELS.items()},
        barmode="group",
        labels={"valor": titulo_y, "VIGENCIA": "Vigencia", "label": "Bloque / Escenario"},
    )
    fig.update_layout(
        **LAYOUT_DEFAULTS,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11)),
        xaxis=dict(tickmode="linear"),
        height=370,
    )
    return fig


# ── Naturaleza Institucional ──────────────────────────────────────────────

def chart_naturaleza_institucional(df: pd.DataFrame, metrica: str = "entidades") -> go.Figure:
    grp = df.groupby("NATURALEZA_INSTITUCIONAL", observed=True)
    if metrica == "entidades":
        data = grp["NOMBRE_ENTIDAD"].nunique().reset_index(name="valor")
        titulo_x = "N° de Entidades Únicas"
    elif metrica == "valor":
        data = (grp["VALOR_REAL_CUANTIA"].sum() / 1e12).reset_index(name="valor")
        titulo_x = "Cuantía Real (Billones COP)"
    else:
        data = grp["CANTIDAD_PROCESOS"].sum().reset_index(name="valor")
        titulo_x = "N° de Procesos SECOP I"

    data = data.sort_values("valor", ascending=True)
    fmt = "%{x:,.2f} B" if metrica == "valor" else "%{x:,}"

    fig = go.Figure(go.Bar(
        x=data["valor"],
        y=data["NATURALEZA_INSTITUCIONAL"],
        orientation="h",
        marker=dict(
            color=data["valor"],
            colorscale=[[0, "#DCE7F3"], [0.5, CCE_AZUL], [1, CCE_VINO_OSCURO]],
            showscale=False,
        ),
        text=data["valor"].apply(lambda v: f"${v:,.2f}B" if metrica == "valor" else f"{int(v):,}"),
        textposition="outside",
        hovertemplate=f"<b>%{{y}}</b><br>{titulo_x}: {fmt}<extra></extra>",
    ))
    fig.update_layout(
        **LAYOUT_DEFAULTS,
        xaxis_title=titulo_x,
        yaxis_title="",
        height=380,
    )
    return fig


# ── Barras horizontales Top N entidades ──────────────────────────────────

def chart_top_entidades(df: pd.DataFrame, n: int = 20, por: str = "procesos") -> go.Figure:
    grp = df.groupby("NOMBRE_ENTIDAD", observed=True)
    if por in ("procesos", "contratos"):
        top = grp["CANTIDAD_PROCESOS"].sum().reset_index(name="valor").nlargest(n, "valor")
        titulo_x = "N° de Procesos en SECOP I"
        hover_val = "%{x:,}"
    else:
        top = (grp["VALOR_REAL_CUANTIA"].sum() / 1e12).reset_index(name="valor").nlargest(n, "valor")
        titulo_x = "Cuantía Real Contratada (Billones COP)"
        hover_val = "$%{x:,.3f} Billones"

    top = top.sort_values("valor")
    top["entidad_corta"] = top["NOMBRE_ENTIDAD"].astype(str).str[:55]

    fig = go.Figure(go.Bar(
        x=top["valor"],
        y=top["entidad_corta"],
        customdata=top[["NOMBRE_ENTIDAD"]],
        orientation="h",
        marker_color=CCE_AZUL if por in ("procesos", "contratos") else CCE_NARANJA,
        hovertemplate="<b>%{customdata[0]}</b><br>" + titulo_x + ": " + hover_val + "<extra></extra>",
    ))
    fig.update_layout(
        **LAYOUT_DEFAULTS,
        xaxis_title=titulo_x,
        yaxis_title="",
        height=max(420, n * 26),
    )
    return fig


# ── Torta / Barras modalidad ──────────────────────────────────────────────

def chart_modalidad(df: pd.DataFrame, tipo: str = "pie") -> go.Figure:
    col_mod = "MODALIDAD_AGRUPADA" if "MODALIDAD_AGRUPADA" in df.columns else "MODALIDAD_CONTRATACION"
    counts = (
        df.groupby(col_mod, observed=True)["CANTIDAD_PROCESOS"]
        .sum()
        .reset_index(name="procesos")
        .sort_values("procesos", ascending=False)
        .head(10)
    )
    counts.columns = ["modalidad", "procesos"]
    counts["modalidad_trunc"] = counts["modalidad"].apply(
        lambda x: x[:42] + "..." if isinstance(x, str) and len(x) > 42 else x
    )

    paleta = [CCE_AZUL, CCE_ROJO, CCE_NARANJA, CCE_MORADO, CCE_GRIS_AZUL, CCE_AMARILLO, CCE_VINO_OSCURO, CCE_CAFE, "#2E86C1", "#7D3C98"]

    if tipo == "pie":
        fig = px.pie(
            counts,
            names="modalidad_trunc",
            values="procesos",
            color_discrete_sequence=paleta,
            hole=0.42,
            hover_data=["modalidad"],
        )
        fig.update_traces(textinfo="percent", textposition="inside")
        fig.update_layout(
            **LAYOUT_DEFAULTS,
            showlegend=True,
            legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
            height=400,
        )
    else:
        counts = counts.sort_values("procesos")
        fig = go.Figure(go.Bar(
            x=counts["procesos"],
            y=counts["modalidad_trunc"],
            orientation="h",
            marker_color=CCE_AZUL,
            hovertemplate="<b>%{customdata[0]}</b><br>Procesos: %{x:,}<extra></extra>",
            customdata=counts[["modalidad"]],
        ))
        fig.update_layout(**LAYOUT_DEFAULTS, showlegend=False, xaxis_title="N° de Procesos", height=400)

    return fig


# ── Barras Top departamentos ──────────────────────────────────────────────

def chart_top_departamentos(df: pd.DataFrame, n: int = 15, por: str = "entidades") -> go.Figure:
    df_valid = df[df["DEPARTAMENTO"] != "No Determinado"]
    grp = df_valid.groupby("DEPARTAMENTO", observed=True)

    if por == "valor":
        top = (grp["VALOR_REAL_CUANTIA"].sum() / 1e12).reset_index(name="valor").nlargest(n, "valor").sort_values("valor")
        titulo_x = "Cuantía Real (Billones COP)"
        hover_fmt = "$%{x:,.2f} Billones"
    elif por == "entidades":
        top = grp["NOMBRE_ENTIDAD"].nunique().reset_index(name="valor").nlargest(n, "valor").sort_values("valor")
        titulo_x = "N° de Entidades Únicas"
        hover_fmt = "%{x:,} entidades"
    else:
        top = grp["CANTIDAD_PROCESOS"].sum().reset_index(name="valor").nlargest(n, "valor").sort_values("valor")
        titulo_x = "N° de Procesos SECOP I"
        hover_fmt = "%{x:,} procesos"

    fig = go.Figure(go.Bar(
        x=top["valor"],
        y=top["DEPARTAMENTO"],
        orientation="h",
        marker=dict(
            color=top["valor"],
            colorscale=[[0, "#DCE7F3"], [0.6, CCE_AZUL], [1, CCE_ROJO]],
            showscale=False,
        ),
        hovertemplate=f"<b>%{{y}}</b><br>{titulo_x}: {hover_fmt}<extra></extra>",
    ))
    fig.update_layout(
        **LAYOUT_DEFAULTS,
        xaxis_title=titulo_x,
        yaxis_title="",
        height=max(400, n * 28),
    )
    return fig


# ── MAPA DE CALOR 1: DEPARTAMENTOS (Coroplético + Densidad) ──────────────

def aggregate_departamentos(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega métricas clave por departamento para mapas y tablas."""
    df_d = df[df["DEPARTAMENTO"].notna() & (df["DEPARTAMENTO"] != "No Determinado")].copy()
    if df_d.empty:
        return pd.DataFrame()

    # Calcular entidades que publican en SECOP II por departamento
    ent_s2 = (
        df_d.drop_duplicates(subset=["DEPARTAMENTO", "NOMBRE_ENTIDAD"])
        .groupby("DEPARTAMENTO", observed=True)
        .agg(
            entidades=("NOMBRE_ENTIDAD", "nunique"),
            entidades_s2=("TIENE_PUBLICACIONES_SECOP2", lambda s: (s == "Sí").sum()),
            nits_homologados=("NIT_HOMOLOGADO", lambda s: s[s != "Sin NIT Válido"].nunique()),
        )
        .reset_index()
    )

    agg = (
        df_d.groupby(["COD_DPTO", "DEPARTAMENTO"], observed=True)
        .agg(
            procesos=("CANTIDAD_PROCESOS", "sum"),
            valor_billones=("VALOR_REAL_CUANTIA", lambda s: s.sum() / 1e12),
            municipios=("MUNICIPIO", "nunique"),
            penetracion_mintic=("PENETRACION_INTERNET_MINTIC", lambda s: s.mean() * 100.0),
            lat=("LATITUD", "mean"),
            lon=("LONGITUD", "mean"),
        )
        .reset_index()
    )
    agg = agg.merge(ent_s2, on="DEPARTAMENTO", how="left")
    agg["pct_secop2"] = np.where(agg["entidades"] > 0, agg["entidades_s2"] / agg["entidades"] * 100.0, 0.0)
    return agg


def chart_mapa_calor_departamentos(
    df: pd.DataFrame,
    geojson_depto: dict,
    metrica: str = "entidades",
    escala_nombre: str = "Institucional CCE (Azul-Naranja-Rojo)",
    estilo_mapa: str = "carto-positron",
) -> go.Figure:
    """
    Mapa de calor coroplético interactivo de los 33 departamentos de Colombia.
    """
    agg = aggregate_departamentos(df)
    if agg.empty:
        return go.Figure()

    metric_cfg = {
        "entidades":   ("entidades", "Entidades Únicas", ",.0f"),
        "procesos":    ("procesos", "Procesos SECOP I", ",.0f"),
        "valor":       ("valor_billones", "Cuantía Real ($ Billones)", ",.2f"),
        "penetracion": ("penetracion_mintic", "Internet Fijo MinTIC (%)", ".1f"),
        "pct_secop2":  ("pct_secop2", "% Entidades en SECOP II", ".1f"),
    }
    col_z, label_z, fmt_z = metric_cfg.get(metrica, metric_cfg["entidades"])
    colorscale = COLOR_SCALES.get(escala_nombre, "YlOrRd")

    customdata = np.stack([
        agg["DEPARTAMENTO"],
        agg["entidades"],
        agg["nits_homologados"],
        agg["procesos"],
        agg["valor_billones"],
        agg["municipios"],
        agg["penetracion_mintic"].fillna(0),
        agg["pct_secop2"].fillna(0),
    ], axis=-1)

    fig = go.Figure(go.Choroplethmapbox(
        geojson=geojson_depto,
        locations=agg["COD_DPTO"],
        featureidkey="id",
        z=agg[col_z],
        colorscale=colorscale,
        marker_opacity=0.82,
        marker_line_width=1.2,
        marker_line_color="#FFFFFF",
        colorbar=dict(
            title=dict(text=label_z, font=dict(size=12, color=CCE_AZUL)),
            thickness=16,
            len=0.75,
        ),
        customdata=customdata,
        hovertemplate=(
            "<b>🏛️ %{customdata[0]}</b><br>"
            "──────────────────────────<br>"
            "• <b>Entidades Únicas:</b> %{customdata[1]:,}<br>"
            "• <b>NITs Homologados:</b> %{customdata[2]:,}<br>"
            "• <b>Procesos SECOP I:</b> %{customdata[3]:,}<br>"
            "• <b>Cuantía Real:</b> $%{customdata[4]:,.2f} Billones COP<br>"
            "• <b>Municipios con Entidades:</b> %{customdata[5]:,}<br>"
            "• <b>Internet Fijo MinTIC:</b> %{customdata[6]:.1f}%<br>"
            "• <b>Publican en SECOP II:</b> %{customdata[7]:.1f}%<extra></extra>"
        ),
    ))

    # Si hay pocos departamentos filtrados, hacer auto-zoom
    if len(agg) == 1:
        center = dict(lat=float(agg["lat"].iloc[0]), lon=float(agg["lon"].iloc[0]))
        zoom = 6.5
    elif len(agg) <= 4:
        center = dict(lat=float(agg["lat"].mean()), lon=float(agg["lon"].mean()))
        zoom = 5.6
    else:
        center = dict(lat=4.5709, lon=-74.2973)
        zoom = 4.6

    fig.update_layout(
        mapbox_style=estilo_mapa,
        mapbox_zoom=zoom,
        mapbox_center=center,
        margin=dict(l=0, r=0, t=10, b=0),
        height=580,
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Arial, sans-serif"),
    )
    return fig


# ── MAPA DE CALOR 2: MUNICIPIOS (Densidad + Puntos / Coroplético / Burbujas) ──

def aggregate_municipios(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega métricas clave a nivel municipal (CODIGO_DIVIPOLA_MAPA)."""
    df_m = df[
        df["CODIGO_DIVIPOLA_MAPA"].notna()
        & (df["CODIGO_DIVIPOLA_MAPA"] != "00000")
        & df["LATITUD"].notna()
        & df["LONGITUD"].notna()
    ].copy()
    if df_m.empty:
        return pd.DataFrame()

    ent_s2 = (
        df_m.drop_duplicates(subset=["CODIGO_DIVIPOLA_MAPA", "NOMBRE_ENTIDAD"])
        .groupby("CODIGO_DIVIPOLA_MAPA", observed=True)
        .agg(
            entidades=("NOMBRE_ENTIDAD", "nunique"),
            entidades_s2=("TIENE_PUBLICACIONES_SECOP2", lambda s: (s == "Sí").sum()),
            nits_homologados=("NIT_HOMOLOGADO", lambda s: s[s != "Sin NIT Válido"].nunique()),
        )
        .reset_index()
    )

    agg = (
        df_m.groupby(["CODIGO_DIVIPOLA_MAPA", "DEPARTAMENTO", "MUNICIPIO"], observed=True)
        .agg(
            procesos=("CANTIDAD_PROCESOS", "sum"),
            valor_billones=("VALOR_REAL_CUANTIA", lambda s: s.sum() / 1e12),
            valor_mm=("VALOR_REAL_CUANTIA", lambda s: s.sum() / 1e9),
            categoria_cgn=("CATEGORIA_CGN", lambda s: s.mode().iloc[0] if not s.mode().empty else "Sexta"),
            penetracion_mintic=("PENETRACION_INTERNET_MINTIC", lambda s: s.mean() * 100.0),
            rango_mintic=("RANGO_CONECTIVIDAD_MINTIC", lambda s: s.mode().iloc[0] if not s.mode().empty else "N/D"),
            lat=("LATITUD", "first"),
            lon=("LONGITUD", "first"),
        )
        .reset_index()
    )
    agg = agg.merge(ent_s2, on="CODIGO_DIVIPOLA_MAPA", how="left")
    agg["pct_secop2"] = np.where(agg["entidades"] > 0, agg["entidades_s2"] / agg["entidades"] * 100.0, 0.0)
    return agg


def chart_mapa_calor_municipios(
    df: pd.DataFrame,
    geojson_mpio: dict = None,
    metrica: str = "entidades",
    modo: str = "densidad",
    escala_nombre: str = "Institucional CCE (Azul-Naranja-Rojo)",
    estilo_mapa: str = "carto-positron",
) -> go.Figure:
    """
    Mapa de Calor Geográfico de los Municipios de Colombia (1.076+ municipios con DIVIPOLA).
    Soporta 3 modos:
      - 'densidad': Mapa de Calor continuo (Densitymapbox) + Puntos interactivos por municipio
      - 'coropletico': Polígonos municipales coloreados según la métrica (Choroplethmapbox)
      - 'burbujas': Burbujas georreferenciadas escaladas y coloreadas por municipio
    """
    agg = aggregate_municipios(df)
    if agg.empty:
        return go.Figure()

    metric_cfg = {
        "entidades":   ("entidades", "Entidades Únicas"),
        "procesos":    ("procesos", "Procesos SECOP I"),
        "valor":       ("valor_mm", "Cuantía Real ($ Miles de Millones)"),
        "penetracion": ("penetracion_mintic", "Internet Fijo MinTIC (%)"),
        "pct_secop2":  ("pct_secop2", "% Entidades en SECOP II"),
    }
    col_z, label_z = metric_cfg.get(metrica, metric_cfg["entidades"])
    colorscale = COLOR_SCALES.get(escala_nombre, "YlOrRd")

    customdata = np.stack([
        agg["MUNICIPIO"],
        agg["DEPARTAMENTO"],
        agg["CODIGO_DIVIPOLA_MAPA"],
        agg["categoria_cgn"],
        agg["entidades"],
        agg["procesos"],
        agg["valor_mm"],
        agg["penetracion_mintic"].fillna(0),
        agg["pct_secop2"].fillna(0),
    ], axis=-1)

    hover_template = (
        "<b>📍 %{customdata[0]} (%{customdata[1]})</b><br>"
        "Código DIVIPOLA: <b>%{customdata[2]}</b> | Cat. CGN: <b>%{customdata[3]}</b><br>"
        "──────────────────────────<br>"
        "• <b>Entidades Únicas:</b> %{customdata[4]:,}<br>"
        "• <b>Procesos SECOP I:</b> %{customdata[5]:,}<br>"
        "• <b>Cuantía Real:</b> $%{customdata[6]:,.1f} Miles de Millones COP<br>"
        "• <b>Internet Fijo MinTIC:</b> %{customdata[7]:.1f}%<br>"
        "• <b>Publican en SECOP II:</b> %{customdata[8]:.1f}%<extra></extra>"
    )

    n_deptos = agg["DEPARTAMENTO"].nunique()
    if n_deptos == 1:
        center = dict(lat=float(agg["lat"].mean()), lon=float(agg["lon"].mean()))
        zoom = 6.9
        radius_heat = 28
    elif n_deptos <= 4:
        center = dict(lat=float(agg["lat"].mean()), lon=float(agg["lon"].mean()))
        zoom = 5.8
        radius_heat = 22
    else:
        center = dict(lat=4.5709, lon=-74.2973)
        zoom = 4.65
        radius_heat = 17

    fig = go.Figure()

    if modo == "coropletico" and geojson_mpio and geojson_mpio.get("features"):
        # Si hay pocos departamentos filtrados, filtrar features del GeoJSON para renderizado instantáneo
        if n_deptos <= 6:
            valid_codes = set(agg["CODIGO_DIVIPOLA_MAPA"].unique())
            sub_geo = {
                "type": "FeatureCollection",
                "features": [f for f in geojson_mpio["features"] if f.get("id") in valid_codes],
            }
        else:
            sub_geo = geojson_mpio

        fig.add_trace(go.Choroplethmapbox(
            geojson=sub_geo,
            locations=agg["CODIGO_DIVIPOLA_MAPA"],
            featureidkey="id",
            z=agg[col_z],
            colorscale=colorscale,
            marker_opacity=0.82,
            marker_line_width=0.5,
            marker_line_color="rgba(255,255,255,0.6)",
            colorbar=dict(
                title=dict(text=label_z, font=dict(size=12, color=CCE_AZUL)),
                thickness=16,
                len=0.75,
            ),
            customdata=customdata,
            hovertemplate=hover_template,
        ))

    elif modo == "burbujas":
        vals = agg[col_z].clip(lower=0).fillna(0)
        max_v = vals.max() if vals.max() > 0 else 1
        sizes = 6 + 24 * np.sqrt(vals / max_v)

        fig.add_trace(go.Scattermapbox(
            lat=agg["lat"],
            lon=agg["lon"],
            mode="markers",
            marker=dict(
                size=sizes,
                color=agg[col_z],
                colorscale=colorscale,
                showscale=True,
                opacity=0.82,
                colorbar=dict(
                    title=dict(text=label_z, font=dict(size=12, color=CCE_AZUL)),
                    thickness=16,
                    len=0.75,
                ),
            ),
            customdata=customdata,
            hovertemplate=hover_template,
        ))

    else:
        # Modo por defecto: Mapa de Calor de Densidad (Densitymapbox) + Puntos Municipales interactivos
        fig.add_trace(go.Densitymapbox(
            lat=agg["lat"],
            lon=agg["lon"],
            z=agg[col_z],
            radius=radius_heat,
            colorscale=colorscale,
            opacity=0.78,
            colorbar=dict(
                title=dict(text=label_z, font=dict(size=12, color=CCE_AZUL)),
                thickness=16,
                len=0.75,
            ),
            hoverinfo="skip",
        ))
        fig.add_trace(go.Scattermapbox(
            lat=agg["lat"],
            lon=agg["lon"],
            mode="markers",
            marker=dict(
                size=6 if n_deptos > 4 else 9,
                color=CCE_AZUL,
                opacity=0.65,
            ),
            customdata=customdata,
            hovertemplate=hover_template,
            name="Municipios",
            showlegend=False,
        ))

    fig.update_layout(
        mapbox_style=estilo_mapa,
        mapbox_zoom=zoom,
        mapbox_center=center,
        margin=dict(l=0, r=0, t=10, b=0),
        height=580,
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Arial, sans-serif"),
    )
    return fig


# ── MAPA DE CALOR 3: MATRIZ CRUZADA 2D (Departamento vs Dimensión) ─────────

def chart_matriz_calor_territorial(
    df: pd.DataFrame,
    dim_col: str = "NATURALEZA_INSTITUCIONAL",
    metrica: str = "entidades",
    top_n: int = 18,
) -> go.Figure:
    """
    Matriz de calor 2D cruzando los Top N Departamentos contra Naturaleza Institucional,
    Categoría CGN, Rango Conectividad MinTIC o Escenario 2026.
    """
    df_valid = df[df["DEPARTAMENTO"] != "No Determinado"].copy()
    if df_valid.empty:
        return go.Figure()

    # Seleccionar Top N departamentos según la métrica
    if metrica == "entidades":
        top_deptos = (
            df_valid.groupby("DEPARTAMENTO", observed=True)["NOMBRE_ENTIDAD"]
            .nunique()
            .nlargest(top_n)
            .index.tolist()
        )
        piv = (
            df_valid[df_valid["DEPARTAMENTO"].isin(top_deptos)]
            .groupby(["DEPARTAMENTO", dim_col], observed=True)["NOMBRE_ENTIDAD"]
            .nunique()
            .unstack(fill_value=0)
        )
        unidad = "Entidades"
    elif metrica == "valor":
        top_deptos = (
            df_valid.groupby("DEPARTAMENTO", observed=True)["VALOR_REAL_CUANTIA"]
            .sum()
            .nlargest(top_n)
            .index.tolist()
        )
        piv = (
            (df_valid[df_valid["DEPARTAMENTO"].isin(top_deptos)]
             .groupby(["DEPARTAMENTO", dim_col], observed=True)["VALOR_REAL_CUANTIA"]
             .sum() / 1e9)
            .round(1)
            .unstack(fill_value=0)
        )
        unidad = "Miles de Millones COP"
    else:
        top_deptos = (
            df_valid.groupby("DEPARTAMENTO", observed=True)["CANTIDAD_PROCESOS"]
            .sum()
            .nlargest(top_n)
            .index.tolist()
        )
        piv = (
            df_valid[df_valid["DEPARTAMENTO"].isin(top_deptos)]
            .groupby(["DEPARTAMENTO", dim_col], observed=True)["CANTIDAD_PROCESOS"]
            .sum()
            .unstack(fill_value=0)
        )
        unidad = "Procesos"

    # Ordenar filas según el orden de top_deptos
    piv = piv.reindex([d for d in top_deptos if d in piv.index])

    fig = px.imshow(
        piv,
        text_auto=True,
        aspect="auto",
        color_continuous_scale=[[0.0, "#F8FAFC"], [0.35, "#90B4D4"], [0.7, CCE_AZUL], [1.0, CCE_ROJO]],
        labels=dict(x="", y="Departamento", color=unidad),
    )
    fig.update_layout(
        **LAYOUT_DEFAULTS,
        xaxis_tickangle=-25,
        height=max(460, len(piv) * 28),
    )
    return fig


# ── Rutas de Despliegue 2026 (TD_01B_LISTA_ENTIDADES) ─────────────────────

def chart_rutas_despliegue_2026(df_td1b: pd.DataFrame, metrica: str = "entidades") -> go.Figure:
    if df_td1b.empty:
        return go.Figure()

    col_ruta = "RUTA_CORTA" if "RUTA_CORTA" in df_td1b.columns else "CLASIFICACION_Y_RUTA_DESPLIEGUE_2026"
    grp = df_td1b.groupby(col_ruta, observed=True)

    if metrica == "procesos":
        data = grp["TOTAL_PROCESOS_ORDINARIOS_S1"].sum().reset_index(name="valor")
        titulo_x = "Procesos Ordinarios SECOP I (2023–2025)"
    elif metrica == "valor":
        data = (grp["VALOR_REAL_CUANTIA_S1"].sum() / 1e12).reset_index(name="valor")
        titulo_x = "Cuantía Real (Billones COP)"
    else:
        data = grp["NOMBRE_ENTIDAD"].nunique().reset_index(name="valor")
        titulo_x = "N° de Entidades Potenciales (TD_01B)"

    data = data.sort_values("valor", ascending=True)
    palette = [CCE_ROJO, CCE_NARANJA, CCE_MORADO, CCE_AZUL, CCE_GRIS_AZUL, CCE_VINO_OSCURO]

    fig = go.Figure(go.Bar(
        x=data["valor"],
        y=data[col_ruta],
        orientation="h",
        marker_color=palette[:len(data)],
        text=data["valor"].apply(lambda v: f"${v:,.2f}B" if metrica == "valor" else f"{int(v):,}"),
        textposition="outside",
        hovertemplate=f"<b>%{{y}}</b><br>{titulo_x}: %{{x:,}}<extra></extra>",
    ))
    fig.update_layout(
        **LAYOUT_DEFAULTS,
        xaxis_title=titulo_x,
        yaxis_title="",
        height=380,
    )
    return fig


# ── Gauge de cumplimiento ─────────────────────────────────────────────────

def chart_gauge_cumplimiento(porcentaje: float, titulo: str = "Entidades en SECOP II", meta: float = 70.0) -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=porcentaje,
        number=dict(suffix="%", valueformat=".1f", font=dict(size=34, color=CCE_AZUL)),
        title=dict(text=titulo, font=dict(size=13, color=CCE_GRIS)),
        gauge=dict(
            axis=dict(range=[0, 100], tickcolor=CCE_GRIS),
            bar=dict(color=CCE_AZUL),
            steps=[
                dict(range=[0, 40],  color="#FDECEA"),
                dict(range=[40, 70], color="#FEF9E7"),
                dict(range=[70, 100], color="#EAFAF1"),
            ],
            threshold=dict(line=dict(color=CCE_ROJO, width=4), thickness=0.75, value=meta),
        ),
    ))
    fig.update_layout(**LAYOUT_DEFAULTS, height=260)
    return fig
