import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np


LANE_COLORS = ["#00d2ff", "#ff6b35", "#00e676", "#ffd600"]
VEHICLE_COLORS = ["#3b82f6", "#f59e0b", "#10b981", "#ef4444"]
DARK_BG = "#0f1117"
CARD_BG = "#1a1d2e"
BORDER = "#2a2d3e"


def dark_layout(fig, title="", height=380):
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color="#e2e8f0", family="'Rajdhani', sans-serif")),
        height=height,
        paper_bgcolor=CARD_BG,
        plot_bgcolor=CARD_BG,
        font=dict(color="#94a3b8", family="'Rajdhani', sans-serif"),
        margin=dict(l=40, r=20, t=50, b=40),
        xaxis=dict(gridcolor=BORDER, showgrid=True, zeroline=False),
        yaxis=dict(gridcolor=BORDER, showgrid=True, zeroline=False),
    )
    return fig


def get_dashboard_charts(lanes, history):
    if not lanes:
        return []

    values = [sum(lane.counts.values()) for lane in lanes]
    lane_labels = [f"Lane {i+1}" for i in range(4)]
    vehicle_types = ["car", "motorcycle", "bus", "truck"]
    type_totals = [sum(lane.counts.get(v, 0) for lane in lanes) for v in vehicle_types]
    accidents = [1 if lane.accident else 0 for lane in lanes]
    signals = [lane.signal_state for lane in lanes]
    figs = []

    # ── 1. Traffic Trend Line Chart ──────────────────────────────────────────
    fig1 = go.Figure()
    for i, lane in enumerate(lanes):
        hist = lane.count_history if lane.count_history else [0]
        fig1.add_trace(go.Scatter(
            y=hist,
            x=list(range(len(hist))),
            mode="lines",
            name=f"Lane {i+1}",
            line=dict(color=LANE_COLORS[i], width=2.5, shape="spline"),
            fill="tozeroy",
        ))
    dark_layout(fig1, "📈  Traffic Volume Trend (Last 60 Frames)")
    fig1.update_xaxes(title_text="Frame", title_font_color="#64748b")
    fig1.update_yaxes(title_text="Vehicle Count", title_font_color="#64748b")
    figs.append(fig1)

    # ── 2. Lane Load Grouped Bar ──────────────────────────────────────────────
    fig2 = go.Figure()
    for vi, vtype in enumerate(vehicle_types):
        fig2.add_trace(go.Bar(
            name=vtype.capitalize(),
            x=lane_labels,
            y=[lane.counts.get(vtype, 0) for lane in lanes],
            marker_color=VEHICLE_COLORS[vi],
            marker_line_color=DARK_BG,
            marker_line_width=1.5,
        ))
    fig2.update_layout(barmode="stack")
    dark_layout(fig2, "🚗  Stacked Vehicle Count per Lane")
    figs.append(fig2)

    # ── 3. Vehicle Types Donut ─────────────────────────────────────────────────
    fig3 = go.Figure(data=[go.Pie(
        labels=[v.capitalize() for v in vehicle_types],
        values=type_totals,
        hole=0.55,
        marker=dict(colors=VEHICLE_COLORS, line=dict(color=DARK_BG, width=2)),
        textinfo="label+percent",
        insidetextfont=dict(color="#e2e8f0"),
    )])
    fig3.update_layout(
        title=dict(text="🚙  Fleet Composition", font=dict(size=16, color="#e2e8f0")),
        height=380,
        paper_bgcolor=CARD_BG,
        plot_bgcolor=CARD_BG,
        font=dict(color="#94a3b8"),
        margin=dict(l=20, r=20, t=50, b=20),
        showlegend=True,
        legend=dict(font=dict(color="#94a3b8")),
    )
    figs.append(fig3)

    # ── 4. Signal State Indicator Cards ───────────────────────────────────────
    sig_colors_map = {"GREEN": "#00e676", "YELLOW": "#ffd600", "RED": "#ff1744"}
    fig4 = go.Figure()
    for i, (lane, sig) in enumerate(zip(lanes, signals)):
        fig4.add_trace(go.Indicator(
            mode="number+delta",
            value=sum(lane.counts.values()),
            number=dict(font=dict(color=sig_colors_map.get(sig, "#94a3b8"), size=40)),
            title=dict(
                text=f'Lane {i+1}<br><span style="font-size:14px;color:{sig_colors_map.get(sig, "#94a3b8")}">{sig}</span>',
                font=dict(size=14, color="#94a3b8")
            ),
            domain=dict(x=[i * 0.25, (i + 1) * 0.25 - 0.02], y=[0, 1]),
        ))
    fig4.update_layout(
        title=dict(text="🚦  Live Signal Status & Vehicle Count", font=dict(size=16, color="#e2e8f0")),
        height=220,
        paper_bgcolor=CARD_BG,
        plot_bgcolor=CARD_BG,
        margin=dict(l=10, r=10, t=50, b=10),
    )
    figs.append(fig4)

    # ── 5. Accident Risk Gauge ─────────────────────────────────────────────────
    risk = sum(accidents) * 25
    fig5 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk,
        title=dict(text="🚨  Accident Risk Score", font=dict(size=16, color="#e2e8f0")),
        number=dict(suffix="%", font=dict(color="#e2e8f0", size=42)),
        gauge=dict(
            axis=dict(range=[0, 100], tickcolor="#94a3b8", tickfont=dict(color="#94a3b8")),
            bar=dict(color="#ef4444"),
            bgcolor=BORDER,
            bordercolor=BORDER,
            steps=[
                dict(range=[0, 33], color="#0a3d1f"),
                dict(range=[33, 66], color="#3d2d00"),
                dict(range=[66, 100], color="#3d0a0a"),
            ],
            threshold=dict(line=dict(color="#ff1744", width=4), thickness=0.75, value=75),
        ),
    ))
    fig5.update_layout(
        height=300,
        paper_bgcolor=CARD_BG,
        plot_bgcolor=CARD_BG,
        font=dict(color="#94a3b8"),
        margin=dict(l=30, r=30, t=60, b=20),
    )
    figs.append(fig5)

    return figs

