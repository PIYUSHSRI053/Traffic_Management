import streamlit as st
import time

# ─── Page config (must be first) ─────────────────────────────────────────────
st.set_page_config(
    page_title="AI Smart Traffic Control",
    layout="wide",
    page_icon="🚦",
    initial_sidebar_state="expanded",
)

from lane import Lane
from config import MIN_GREEN, MAX_GREEN, YELLOW_TIME
from dashboard import get_dashboard_charts
from evaluator import get_evaluation_metrics
from vision_utils import create_placeholder_frame, cv2_error_message, has_cv2

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Removed Google Fonts import */

/* Global dark theme */
html, body, .stApp {
    background-color: #0a0e1a !important;
    color: #c9d1e0 !important;
    font-family: 'Rajdhani', sans-serif !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1120 0%, #0a0e1a 100%) !important;
    border-right: 1px solid #1e2540 !important;
}
[data-testid="stSidebar"] * { color: #c9d1e0 !important; }

/* Headers */
h1, h2, h3, h4, h5 {
    font-family: 'Rajdhani', sans-serif !important;
    letter-spacing: 1px !important;
}

/* Main title */
.main-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2.6rem;
    font-weight: 700;
    letter-spacing: 3px;
    background: linear-gradient(135deg, #00d2ff, #7b2ff7, #00e676);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-transform: uppercase;
    margin-bottom: 0;
}

.subtitle {
    color: #4a6080;
    font-size: 0.95rem;
    letter-spacing: 4px;
    text-transform: uppercase;
    margin-top: 0;
    font-family: 'Share Tech Mono', monospace;
}

/* Lane card */
.lane-card {
    background: linear-gradient(145deg, #111828, #0e1520);
    border: 1px solid #1e2a40;
    border-radius: 16px;
    padding: 16px;
    transition: border-color 0.3s;
}
.lane-card-green { border-color: #00e676 !important; box-shadow: 0 0 20px rgba(0,230,118,0.15); }
.lane-card-red   { border-color: #ff1744 !important; }
.lane-card-yellow{ border-color: #ffd600 !important; box-shadow: 0 0 20px rgba(255,214,0,0.1); }

.lane-label {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #7090b0;
    margin-bottom: 8px;
    text-align: center;
}

/* Signal text badge */
.sig-badge {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 3px;
    text-align: center;
    padding: 4px 0 6px;
}

/* Vehicle metric cards */
.veh-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 6px;
    margin-top: 10px;
}
.veh-metric {
    background: #0d1422;
    border: 1px solid #1a2235;
    border-radius: 8px;
    padding: 6px 8px;
    text-align: center;
}
.veh-metric .veh-label { font-size: 0.65rem; color: #4a6080; letter-spacing: 1px; text-transform: uppercase; }
.veh-metric .veh-value { font-size: 1.2rem; font-weight: 700; color: #e2e8f0; font-family: 'Share Tech Mono', monospace; }

/* Total badge */
.total-badge {
    background: linear-gradient(135deg, #0d1e35, #111828);
    border: 1px solid #1e3050;
    border-radius: 10px;
    padding: 8px;
    text-align: center;
    margin: 8px 0;
}
.total-badge .tb-label { font-size: 0.65rem; color: #4a6080; letter-spacing: 2px; text-transform: uppercase; }
.total-badge .tb-value { font-size: 1.8rem; font-weight: 700; color: #00d2ff; font-family: 'Share Tech Mono', monospace; }

/* Accident alert */
.accident-alert {
    background: linear-gradient(135deg, #1a0808, #2a0a0a);
    border: 1px solid #ff1744;
    border-radius: 10px;
    padding: 8px 12px;
    text-align: center;
    font-size: 0.8rem;
    color: #ff6b6b;
    letter-spacing: 2px;
    /* animation removed */;
    font-family: 'Share Tech Mono', monospace;
}
/* Removed pulse-red animation */

/* Timer bar */
.timer-container {
    background: #0d1422;
    border: 1px solid #1a2235;
    border-radius: 8px;
    padding: 8px 12px;
    margin: 8px 0;
}
.timer-label { font-size: 0.7rem; color: #4a6080; letter-spacing: 2px; text-transform: uppercase; }
.timer-value { font-size: 1.4rem; font-weight: 700; font-family: 'Share Tech Mono', monospace; color: #ffd600; }

/* Upload zone */
.upload-hint {
    background: #0d1422;
    border: 1px dashed #1e3050;
    border-radius: 10px;
    padding: 12px;
    text-align: center;
    color: #4a6080;
    font-size: 0.8rem;
    letter-spacing: 1px;
    margin-bottom: 6px;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #0d1e35, #0a1628) !important;
    color: #00d2ff !important;
    border: 1px solid #1e3a5f !important;
    border-radius: 8px !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    border-color: #00d2ff !important;
    box-shadow: 0 0 12px rgba(0,210,255,0.2) !important;
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    background: #0d1120 !important;
    border-bottom: 1px solid #1e2540 !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #4a6080 !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    padding: 10px 24px !important;
    border-bottom: 2px solid transparent !important;
}
.stTabs [aria-selected="true"] {
    color: #00d2ff !important;
    border-bottom: 2px solid #00d2ff !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab-panel"] {
    background: #0a0e1a !important;
    padding-top: 20px !important;
}

/* Divider */
hr { border-color: #1e2540 !important; }

/* Metrics */
[data-testid="stMetric"] {
    background: #111828 !important;
    border: 1px solid #1e2a40 !important;
    border-radius: 10px !important;
    padding: 10px !important;
}
[data-testid="stMetricLabel"] { color: #4a6080 !important; font-size: 0.7rem !important; letter-spacing: 1px !important; }
[data-testid="stMetricValue"] { color: #e2e8f0 !important; font-family: 'Share Tech Mono', monospace !important; }

/* DataFrame */
[data-testid="stDataFrame"] { border: 1px solid #1e2540 !important; border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)


# ─── Traffic Light SVG ────────────────────────────────────────────────────────
def traffic_light_svg(signal: str) -> str:
    """
    Returns an SVG traffic light.
    Active light glows; inactive lights are dark.
    """
    def light(color_hex: str, active: bool) -> str:
        return f"""
    <circle cx="40" cy="0" r="22"
        fill="{color_hex if active else '#0a0e1a'}"
        stroke="#1e2540" stroke-width="2"/>
    <circle cx="40" cy="0" r="14"
        fill="{color_hex if active else '#1e2540'}" opacity="0.08"/>
    """

    red_on = signal == "RED"
    yellow_on = signal == "YELLOW"
    green_on = signal == "GREEN"

    housing_color = "#0d1422" if signal != "GREEN" else "#0d1a15"
    border_color = (
        "#ff1744" if red_on else "#ffd600" if yellow_on else "#00e676" if green_on else "#1e2540"
    )
    sig_text_color = "#ff1744" if red_on else "#ffd600" if yellow_on else "#00e676"

    return f"""
<svg viewBox="0 0 80 260" xmlns="http://www.w3.org/2000/svg" width="80" height="260">
  <defs>
    <linearGradient id="housing" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{housing_color}"/>
      <stop offset="100%" stop-color="#080c14"/>
    </linearGradient>
  </defs>

  <rect x="10" y="10" width="60" height="240" rx="18"
        fill="url(#housing)" stroke="{border_color}" stroke-width="2.5"/>

  <circle cx="22" cy="22" r="4" fill="#0d1422" stroke="#1e2540" stroke-width="1.5"/>
  <circle cx="58" cy="22" r="4" fill="#0d1422" stroke="#1e2540" stroke-width="1.5"/>
  <circle cx="22" cy="238" r="4" fill="#0d1422" stroke="#1e2540" stroke-width="1.5"/>
  <circle cx="58" cy="238" r="4" fill="#0d1422" stroke="#1e2540" stroke-width="1.5"/>

  <g transform="translate(0,68)">
    {light("#ff1744", red_on)}
  </g>

  <g transform="translate(0,130)">
    {light("#ffd600", yellow_on)}
  </g>

  <g transform="translate(0,192)">
    {light("#00e676", green_on)}
  </g>

  <text x="40" y="256" text-anchor="middle"
        font-family="'Share Tech Mono', monospace"
        font-size="9" fill="{sig_text_color}" letter-spacing="1">
    {signal}
  </text>
</svg>
"""


# ─── Session state init ───────────────────────────────────────────────────────
def init_state():
    if "initialized" not in st.session_state:
        try:
            from ultralytics import YOLO
            model = YOLO("yolov8n.pt")
        except Exception:
            model = None

        st.session_state.model = model
        st.session_state.lanes = []
        for i in range(4):
            pos = "left" if i % 2 == 0 else "right"
            lane = Lane(model, pos, lane_id=i)
            st.session_state.lanes.append(lane)

        st.session_state.current_lane = 0
        st.session_state.signal_state = "GREEN"
        st.session_state.last_switch = time.time()
        st.session_state.history = []

        # Set initial signals
        for i, lane in enumerate(st.session_state.lanes):
            lane.set_signal("GREEN" if i == 0 else "RED")

        st.session_state.initialized = True


def lane_green_time(lane_index: int) -> int:
    lane = st.session_state.lanes[lane_index]
    density = sum(lane.counts.values())
    return max(MIN_GREEN, min(MAX_GREEN, int(MIN_GREEN + density * 0.6)))


def activate_lane(lane_index: int):
    for i, lane in enumerate(st.session_state.lanes):
        lane.set_signal("GREEN" if i == lane_index else "RED")

    st.session_state.current_lane = lane_index
    st.session_state.signal_state = "GREEN"
    st.session_state.last_switch = time.time()


def set_all_red():
    for lane in st.session_state.lanes:
        lane.set_signal("RED")

    st.session_state.signal_state = "RED"
    st.session_state.last_switch = time.time()


# ─── Traffic logic ────────────────────────────────────────────────────────────
def traffic_logic():
    lanes = st.session_state.lanes
    elapsed = time.time() - st.session_state.last_switch
    cur = st.session_state.current_lane

    if st.session_state.signal_state == "GREEN":
        green_time = lane_green_time(cur)
        remaining = max(0, int(green_time - elapsed))

        if elapsed >= green_time:
            lanes[cur].set_signal("YELLOW")
            st.session_state.signal_state = "YELLOW"
            st.session_state.last_switch = time.time()
        return remaining, green_time

    elif st.session_state.signal_state == "YELLOW":
        remaining = max(0, int(YELLOW_TIME - elapsed))
        if elapsed >= YELLOW_TIME:
            next_lane = (cur + 1) % 4
            activate_lane(next_lane)
            next_green_time = lane_green_time(next_lane)
            return next_green_time, next_green_time
        return remaining, YELLOW_TIME

    return 0, 0


# ─── Placeholder image ────────────────────────────────────────────────────────
def placeholder_frame():
    return create_placeholder_frame("NO VIDEO", "Upload a video file")


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    init_state()
    lanes = st.session_state.lanes
    remaining, green_time = traffic_logic()
    cur = st.session_state.current_lane
    sig = st.session_state.signal_state
    badge_color = "#00e676" if sig == "GREEN" else "#ff1744" if sig == "RED" else "#ffd600"
    timer_text = f"{remaining}s" if sig != "RED" else "PAUSED"

    if not has_cv2():
        st.warning(
            "OpenCV could not be imported in this deployment. "
            "The interface can still load, but video uploads and live detection stay disabled "
            "until Streamlit Cloud reinstalls the required system packages."
        )
        error_details = cv2_error_message()
        if error_details:
            st.caption(f"OpenCV import details: `{error_details}`")

    # ── Header ────────────────────────────────────────────────────────────────
    col_title, col_badge = st.columns([4.6, 1.6])
    with col_title:
        st.markdown('<h1 class="main-title">AI Smart Traffic Control</h1    >', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">Real-time vehicle detection & adaptive signal management</p>', unsafe_allow_html=True)
    with col_badge:
        st.markdown(f"""
        <div style="text-align:right; margin-top:8px;">
            <div style="background:#0d1422; border:1px solid {badge_color}; border-radius:12px;
                        padding:10px 14px; display:inline-block; min-width:200px;">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:14px;">
                    <div style="text-align:left;">
                        <div style="font-size:0.65rem; color:#4a6080; letter-spacing:2px; font-family:'Share Tech Mono',monospace;">ACTIVE LANE</div>
                        <div style="font-size:1.5rem; font-weight:700; color:{badge_color}; font-family:'Share Tech Mono',monospace;">LANE {cur+1}</div>
                        <div style="font-size:0.72rem; color:{badge_color}; letter-spacing:2px; font-family:'Share Tech Mono',monospace;">{sig}</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-size:0.65rem; color:#4a6080; letter-spacing:2px; font-family:'Share Tech Mono',monospace;">TIMER</div>
                        <div style="font-size:1.15rem; font-weight:700; color:{badge_color}; font-family:'Share Tech Mono',monospace;">{timer_text}</div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("""
        <div style="font-family:'Rajdhani',sans-serif; font-size:1.3rem; font-weight:700;
                    letter-spacing:3px; color:#00d2ff; text-transform:uppercase; margin-bottom:16px;">
            ⚙ Controls
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**📂 Upload Lane Videos**")
        video_files = {}
        for i in range(4):
            uploaded = st.file_uploader(
                f"Lane {i+1}",
                type=["mp4", "avi", "mov", "mkv"],
                key=f"upload_{i}",
                label_visibility="visible",
            )
            if uploaded:
                video_files[i] = uploaded

        if video_files:
            if st.button("▶  Load Videos", use_container_width=True):
                loaded_count = 0
                failed_lanes = []
                for i, f in video_files.items():
                    if lanes[i].load_uploaded_video(f):
                        loaded_count += 1
                    else:
                        failed_lanes.append(
                            f"Lane {i + 1}: {lanes[i].load_error or 'Unable to load the video.'}"
                        )
                if loaded_count:
                    st.success(f"✅ {loaded_count} video(s) loaded!")
                if failed_lanes:
                    st.error("\n".join(failed_lanes))

        st.markdown("---")
        st.markdown("**🎛️ Manual Controls**")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("⏭ Next Lane", use_container_width=True):
                activate_lane((st.session_state.current_lane + 1) % 4)

        with col2:
            if st.button("🔴 All Red", use_container_width=True):
                set_all_red()

        with col3:
            if st.button("🟢 Green", use_container_width=True):
                activate_lane(st.session_state.current_lane)

        st.markdown("---")
        # Live timer in sidebar
        sig = st.session_state.signal_state
        sig_color = "#00e676" if sig == "GREEN" else "#ff1744" if sig == "RED" else "#ffd600"
        st.markdown(f"""
        <div class="timer-container">
            <div class="timer-label">Current Signal</div>
            <div class="timer-value" style="color:{sig_color};">{sig}</div>
            <div class="timer-label" style="margin-top:4px;">Time Remaining</div>
            <div class="timer-value">{timer_text}</div>
        </div>
        """, unsafe_allow_html=True)

        # Progress bar
        if sig == "GREEN" and green_time > 0:
            progress = max(0.0, min(1.0, remaining / green_time))
            st.progress(progress)

        st.markdown("---")
        st.markdown(f"""
        <div style="font-family:'Share Tech Mono',monospace; font-size:0.7rem; color:#2a3a50; text-align:center; letter-spacing:1px;">
            YOLOv8n · SORT Tracker<br>
            Adaptive Signal Control<br>
            {'✅ Model Loaded' if st.session_state.model else '⚠️ No Model (Demo Mode)'}
        </div>
        """, unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["  🎥  LIVE TRAFFIC  ", "  📊  DASHBOARD  ", "  📈  EVALUATION  "])

    # ── Tab 1: Live Traffic ───────────────────────────────────────────────────
    with tab1:
        # 2x2 Grid Layout for 4 Lanes
        # Row 1: Lane1 | Lane2
        row1_col1, row1_col2 = st.columns(2, gap="large")
        
        # Row 2: Lane3 | Lane4  
        row2_col1, row2_col2 = st.columns(2, gap="large")
        
        def render_lane_display(lane_idx):
            """Helper to render single lane display"""
            lane = lanes[lane_idx]
            sig = lane.signal_state
            sig_color = "#00e676" if sig == "GREEN" else "#ff1744" if sig == "RED" else "#ffd600"
            
            # Lane label
            st.markdown(f'''
            <div style="text-align:center; font-family:'Rajdhani',sans-serif;
                        font-size:0.85rem; font-weight:700; letter-spacing:3px;
                        text-transform:uppercase; color:#4a6080; margin-bottom:4px;">
                ◈ LANE {lane_idx+1}
            </div>
            ''', unsafe_allow_html=True)
    
            # Traffic light SVG
            st.markdown(
                f'<div style="display:flex; justify-content:center; margin:4px 0 8px;">'
                f'{traffic_light_svg(sig)}'
                f'</div>',
                unsafe_allow_html=True
            )
    
            # Signal badge
            st.markdown(f"""
            <div class="sig-badge" style="color:{sig_color}; background: #0d1422;
                 border:1px solid {sig_color}33; border-radius:8px; padding:5px; margin-bottom:8px;">
                ● {sig}
            </div>
            """, unsafe_allow_html=True)
    
            # Video frame
            frame = lane.get_frame()
            if frame is None:
                frame = placeholder_frame()
            st.image(frame, width=800)
    
            # Live/Paused status
            status_color = "#00e676" if sig == "GREEN" else "#4a6080"
            status_text = "▶ LIVE DETECTION" if sig == "GREEN" else "⏸ VIDEO PAUSED"
            st.markdown(f"""
            <div style="text-align:center; font-size:0.7rem; color:{status_color};
                        font-family:'Share Tech Mono',monospace; letter-spacing:2px; margin-top:4px;">
                {status_text}
            </div>""", unsafe_allow_html=True)
    
            # Total vehicles badge
            total = sum(lane.counts.values())
            st.markdown(f"""
            <div class="total-badge">
                <div class="tb-label">Total Vehicles</div>
                <div class="tb-value">{total:02d}</div>
            </div>
            """, unsafe_allow_html=True)
    
            # Vehicle breakdown grid
            st.markdown(f"""
            <div class="veh-grid">
                <div class="veh-metric"><div class="veh-label">🚗 Cars</div><div class="veh-value">{lane.counts['car']:02d}</div></div>
                <div class="veh-metric"><div class="veh-label">🏍 Bikes</div><div class="veh-value">{lane.counts['motorcycle']:02d}</div></div>
                <div class="veh-metric"><div class="veh-label">🚌 Buses</div><div class="veh-value">{lane.counts['bus']:02d}</div></div>
                <div class="veh-metric"><div class="veh-label">🚛 Trucks</div><div class="veh-value">{lane.counts['truck']:02d}</div></div>
            </div>
            """, unsafe_allow_html=True)
    
            # Accident alert
            if lane.accident:
                st.markdown("""
                <div class="accident-alert">⚠ ACCIDENT ALERT (HIGH CONGESTION)</div>
                """, unsafe_allow_html=True)
    
        # Row 1
        with row1_col1:
            render_lane_display(0)  # Lane 1
        with row1_col2:
            render_lane_display(1)  # Lane 2
        
        # Row 2  
        with row2_col1:
            render_lane_display(2)  # Lane 3
        with row2_col2:
            render_lane_display(3)  # Lane 4
    
    with tab2:
        figs = get_dashboard_charts(lanes, st.session_state.history)
        if figs:
            # Row 1: Trend + Stacked Bar
            r1c1, r1c2 = st.columns(2)
            with r1c1:
                st.plotly_chart(figs[0], use_container_width=True)
            with r1c2:
                st.plotly_chart(figs[1], use_container_width=True)
            # Row 2: Donut + Indicators  
            r2c1, r2c2 = st.columns([1, 2])
            with r2c1:
                st.plotly_chart(figs[2], use_container_width=True)
            with r2c2:
                st.plotly_chart(figs[3], use_container_width=True)
            # Row 3: Gauge + Heatmap
            r3c1, r3c2 = st.columns([1, 2])
            with r3c1:
                st.plotly_chart(figs[4], use_container_width=True)
            with r3c2:
                # Live density heatmap
                import plotly.graph_objects as go
                z_data = [[lane.counts.get(v, 0) for v in ["car","motorcycle","bus","truck"]] for lane in lanes]
                fig_heat = go.Figure(go.Heatmap(
                    z=z_data, x=["Car","Bike","Bus","Truck"], y=[f"Lane {i+1}" for i in range(4)],
                    colorscale=[[0,"#0a1628"],[0.5,"#1e40af"],[1,"#00d2ff"]], 
                    text=[[str(v) for v in row] for row in z_data], texttemplate="%{text}",
                    textfont=dict(color="white", size=14), showscale=True
                ))
                fig_heat.update_layout(
                    title=dict(text="🌡️ Live Density Heatmap", font=dict(size=16, color="#e2e8f0")),
                    height=300, paper_bgcolor="#1a1d2e", plot_bgcolor="#1a1d2e", 
                    font=dict(color="#94a3b8", family="'Rajdhani', sans-serif"),
                    margin=dict(l=60, r=20, t=50, b=40)
                )
                st.plotly_chart(fig_heat, use_container_width=True)
    
    
    # ── Tab 3: Evaluation ─────────────────────────────────────────────────────
    with tab3:
        try:
            metrics_df = get_evaluation_metrics(lanes)
            if not metrics_df.empty:
                st.markdown("#### 📋 System Performance Metrics")
                st.dataframe(metrics_df, use_container_width=True, hide_index=True)
            else:
                st.info("📊 No evaluation data yet. Run detection first.")
        except Exception as e:
            st.error(f"Evaluation error: {str(e)}")
    
    # ── Update history & Auto refresh ───────────────────────────────────────────
    # Log current state for dashboard charts
    current_totals = [sum(lane.counts.values()) for lane in lanes]
    st.session_state.history.append({
        'timestamp': time.time(),
        'totals': current_totals,
        'signals': [lane.signal_state for lane in lanes]
    })
    if len(st.session_state.history) > 100:
        st.session_state.history = st.session_state.history[-100:]
    
    time.sleep(0.1)
    st.rerun()


if __name__ == "__main__":
    main()
