"""
Gráficos reutilizables para el Dashboard EMAE – Plotly Express/GO.
Paleta institucional Colombia Compra Eficiente: azul #003F7E + verde #009B3A.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# ── Paleta institucional CCE (Nueva) ────────────────────────────────────────
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

CCE_GRIS    = CCE_GRIS_OSCURO
CCE_CLARO   = "#F5F6F8"
CCE_VERDE   = "#3E546C" # Reemplazo para mantener estructura previa sin romper

ESCENARIO_COLORS = {
    "OBLIGADA_CIRCULAR_Y_LEY80":          CCE_ROJO,
    "OBLIGADA_CIRCULAR_PERO_NO_LEY80":    CCE_NARANJA,
    "NO_CIRCULAR_PERO_LEY80":             CCE_AMARILLO,
    "NO_CIRCULAR_NO_LEY80":               CCE_AZUL,
}

ESCENARIO_LABELS = {
    "OBLIGADA_CIRCULAR_Y_LEY80":          "Obligada + Ley 80",
    "OBLIGADA_CIRCULAR_PERO_NO_LEY80":    "Obligada + Rég. Especial",
    "NO_CIRCULAR_PERO_LEY80":             "No Obligada + Ley 80",
    "NO_CIRCULAR_NO_LEY80":               "No Obligada + Rég. Especial",
}

LAYOUT_DEFAULTS = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, Arial, sans-serif", color="#1A1A2E"),
    margin=dict(l=20, r=20, t=40, b=20),
)


def _label_escenario(s: pd.Series) -> pd.Series:
    return s.map(ESCENARIO_LABELS).fillna(s)


# ── Dona de escenarios ─────────────────────────────────────────────────────

def chart_dona_escenarios(df: pd.DataFrame) -> go.Figure:
    col = "ESCENARIO_REPORTE_FINAL"
    counts = df[col].value_counts().reset_index()
    counts.columns = ["escenario", "contratos"]
    counts["label"] = _label_escenario(counts["escenario"])
    counts["color"] = counts["escenario"].map(ESCENARIO_COLORS).fillna(CCE_GRIS)

    fig = go.Figure(go.Pie(
        labels=counts["label"],
        values=counts["contratos"],
        hole=0.55,
        marker=dict(colors=counts["color"].tolist(), line=dict(color="#fff", width=2)),
        textinfo="label+percent",
        insidetextorientation="auto",
        hovertemplate="<b>%{label}</b><br>Contratos: %{value:,}<br>%{percent}<extra></extra>",
    ))
    fig.update_layout(
        **LAYOUT_DEFAULTS,
        showlegend=False,
        annotations=[dict(text="Escenarios", x=0.5, y=0.5, font_size=14, showarrow=False,
                          font_color=CCE_AZUL, font_family="Inter, Arial, sans-serif")],
    )
    return fig


# ── Barras por escenario y vigencia ───────────────────────────────────────

def chart_barras_escenario_vigencia(df: pd.DataFrame, metrica: str = "contratos") -> go.Figure:
    col_esc = "ESCENARIO_REPORTE_FINAL"
    grp = df.groupby([col_esc, "VIGENCIA"], observed=True)

    if metrica == "contratos":
        data = grp.size().reset_index(name="valor")
        titulo_y = "N° de Contratos"
        fmt = ","
    else:
        data = grp["VALOR_CONTRATO_CON_ADICIONES"].sum().reset_index(name="valor")
        titulo_y = "Valor Contratado (COP)"
        fmt = ",.0f"

    data["label"] = _label_escenario(data[col_esc])
    data["color"] = data[col_esc].map(ESCENARIO_COLORS).fillna(CCE_GRIS)
    data["VIGENCIA"] = data["VIGENCIA"].astype(str)

    fig = px.bar(
        data, x="VIGENCIA", y="valor", color="label",
        color_discrete_map={v: ESCENARIO_COLORS.get(k, CCE_GRIS) for k, v in ESCENARIO_LABELS.items()},
        barmode="group",
        labels={"valor": titulo_y, "VIGENCIA": "Vigencia", "label": "Escenario"},
    )
    fig.update_layout(
        **LAYOUT_DEFAULTS,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(tickmode="linear"),
    )
    return fig


# ── Barras horizontales Top N entidades ──────────────────────────────────

def chart_top_entidades(df: pd.DataFrame, n: int = 20, por: str = "contratos") -> go.Figure:
    if por == "contratos":
        top = (df.groupby("NOMBRE_ENTIDAD_SECOPI", observed=True)
                 .size().reset_index(name="valor")
                 .nlargest(n, "valor"))
        titulo_x = "N° de Contratos"
    else:
        top = (df.groupby("NOMBRE_ENTIDAD_SECOPI", observed=True)
                 ["VALOR_CONTRATO_CON_ADICIONES"].sum().reset_index(name="valor")
                 .nlargest(n, "valor"))
        titulo_x = "Valor Contratado (COP)"

    top = top.sort_values("valor")
    top["NOMBRE_ENTIDAD_SECOPI"] = top["NOMBRE_ENTIDAD_SECOPI"].str[:55]

    fig = go.Figure(go.Bar(
        x=top["valor"],
        y=top["NOMBRE_ENTIDAD_SECOPI"],
        orientation="h",
        marker_color=CCE_AZUL,
        hovertemplate="<b>%{y}</b><br>" + titulo_x + ": %{x:,}<extra></extra>",
    ))
    fig.update_layout(
        **LAYOUT_DEFAULTS,
        xaxis_title=titulo_x,
        yaxis_title="",
        height=max(400, n * 28),
    )
    return fig


# ── Torta / Barras modalidad ──────────────────────────────────────────────

def chart_modalidad(df: pd.DataFrame, tipo: str = "pie") -> go.Figure:
    counts = (df["MODALIDAD_CONTRATACION"]
              .value_counts()
              .head(10)
              .reset_index())
    counts.columns = ["modalidad", "contratos"]
    
    # Truncate long labels to prevent layout squishing
    counts["modalidad_trunc"] = counts["modalidad"].apply(lambda x: x[:40] + "..." if isinstance(x, str) and len(x) > 40 else x)

    paleta = px.colors.sequential.Blues_r[:len(counts)]

    if tipo == "pie":
        fig = px.pie(counts, names="modalidad_trunc", values="contratos",
                     color_discrete_sequence=paleta,
                     hole=0.4,
                     hover_data=["modalidad"])
        fig.update_traces(textinfo="label+percent", textposition="inside")
        fig.update_layout(
            **LAYOUT_DEFAULTS, 
            showlegend=True,
            legend=dict(orientation="h", y=-0.1, x=0.5, xanchor="center") # Move legend to bottom
        )
    else:
        counts = counts.sort_values("contratos")
        fig = go.Figure(go.Bar(
            x=counts["contratos"], y=counts["modalidad_trunc"],
            orientation="h", marker_color=CCE_AZUL,
            hovertemplate="<b>%{customdata[0]}</b><br>Contratos: %{x:,}<extra></extra>",
            customdata=counts[["modalidad"]]
        ))
        fig.update_layout(**LAYOUT_DEFAULTS, showlegend=False)

    return fig


# ── Línea de tiempo contratos por mes ─────────────────────────────────────

def chart_timeline(df: pd.DataFrame) -> go.Figure:
    if "FECHA_FIRMA_CONTRATO" not in df.columns:
        return go.Figure()

    ts = (df.dropna(subset=["FECHA_FIRMA_CONTRATO"])
            .assign(mes=lambda x: x["FECHA_FIRMA_CONTRATO"].dt.to_period("M").dt.to_timestamp())
            .groupby("mes").size().reset_index(name="contratos"))

    fig = go.Figure(go.Scatter(
        x=ts["mes"], y=ts["contratos"],
        mode="lines+markers",
        line=dict(color=CCE_AZUL, width=2.5),
        marker=dict(color=CCE_VERDE, size=5),
        fill="tozeroy",
        fillcolor="rgba(0,63,126,0.12)",
        hovertemplate="<b>%{x|%b %Y}</b><br>Contratos: %{y:,}<extra></extra>",
    ))
    fig.update_layout(
        **LAYOUT_DEFAULTS,
        xaxis_title="Mes",
        yaxis_title="N° de Contratos",
        xaxis=dict(tickformat="%b %Y"),
    )
    return fig


# ── Barras Top departamentos ──────────────────────────────────────────────

def chart_top_departamentos(df: pd.DataFrame, n: int = 15, por: str = "valor") -> go.Figure:
    col_depto = "DEPARTAMENTO_MINTIC" if "DEPARTAMENTO_MINTIC" in df.columns else "DEPARTAMENTO_SECOPI"

    if por == "valor":
        top = (df.groupby(col_depto, observed=True)
                 ["VALOR_CONTRATO_CON_ADICIONES"].sum().reset_index(name="valor")
                 .nlargest(n, "valor").sort_values("valor"))
        titulo_x = "Valor Contratado (COP)"
    else:
        top = (df.groupby(col_depto, observed=True)
                 .size().reset_index(name="valor")
                 .nlargest(n, "valor").sort_values("valor"))
        titulo_x = "N° de Contratos"

    fig = go.Figure(go.Bar(
        x=top["valor"],
        y=top[col_depto],
        orientation="h",
        marker=dict(
            color=top["valor"],
            colorscale=[[0, CCE_CLARO], [1, CCE_AZUL]],
            showscale=False,
        ),
        hovertemplate="<b>%{y}</b><br>" + titulo_x + ": %{x:,}<extra></extra>",
    ))
    fig.update_layout(
        **LAYOUT_DEFAULTS,
        xaxis_title=titulo_x,
        yaxis_title="",
        height=max(400, n * 30),
    )
    return fig


# ── Gauge de cumplimiento ─────────────────────────────────────────────────

def chart_gauge_cumplimiento(porcentaje: float, titulo: str = "Entidades en SECOP II") -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=porcentaje,
        number=dict(suffix="%", font=dict(size=36, color=CCE_AZUL)),
        title=dict(text=titulo, font=dict(size=14, color=CCE_GRIS)),
        gauge=dict(
            axis=dict(range=[0, 100], tickcolor=CCE_GRIS),
            bar=dict(color=CCE_AZUL),
            steps=[
                dict(range=[0, 40],  color="#FDECEA"),
                dict(range=[40, 70], color="#FEF9E7"),
                dict(range=[70, 100],color="#EAFAF1"),
            ],
            threshold=dict(line=dict(color=CCE_VERDE, width=4), thickness=0.75, value=70),
        ),
    ))
    fig.update_layout(**LAYOUT_DEFAULTS, height=280)
    return fig
