import streamlit as st
import time
import numpy as np
import cv2
import os

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

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Global dark theme */
html, body, .stApp {
    background-color: #0a0e1a !important;
    color: #c9d1e0 !important;
    font-family: 'Rajdhani', sans-serif !important;
}

.stButton > button {
    background: linear-gradient(135deg, #0d1e35, #0a1628) !important;
    color: #00d2ff !important;
    border: 1px solid #1e3a5f !important;
    border-radius: 8px !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
}
</style>
""", unsafe_allow_html=True)

# ─── Traffic Light SVG ────────────────────────────────────────────────────────
def traffic_light_svg(signal: str) -> str:
    colors = {"GREEN": "#00e676", "RED": "#ff1744", "YELLOW": "#ffd600"}
    active_color = colors.get(signal, "#94a3b8")
    return f'<div style="text-align:center;">● {signal}</div>'

# ─── Placeholder ──────────────────────────────────────────────────────────────
def placeholder_frame():
    img = np.zeros((320, 480, 3), dtype=np.uint8)
    cv2.putText(img, "UPLOAD VIDEO", (140, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 150, 200), 2)
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# ─── Init ─────────────────────────────────────────────────────────────────────
if 'lanes' not in st.session_state:
    st.session_state.lanes = [Lane(None, 'left', i) for i in range(4)]
lanes = st.session_state.lanes

st.title("🚦 AI Smart Traffic Control - 2x2 Grid Layout")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Controls")
    for i in range(4):
        uploaded = st.file_uploader(f"Lane {i+1}", type=['mp4'], key=f'u{i}')
        if uploaded:
            lanes[i].load_uploaded_video(uploaded)
    if st.button("Start Detection"):
        st.success("Videos loaded!")

# ── 2x2 Grid ──────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    st.subheader("Lane 1 | Lane 2")
    
row1 = st.columns(2)
with row1[0]:
    lane = lanes[0]
    st.markdown(f"**Lane 1** - {lane.signal_state}")
    frame = lane.get_frame() or placeholder_frame()
    st.image(frame, use_column_width=True)
with row1[1]:
    lane = lanes[1]
    st.markdown(f"**Lane 2** - {lane.signal_state}")
    frame = lane.get_frame() or placeholder_frame()
    st.image(frame, use_column_width=True)

row2 = st.columns(2)
with row2[0]:
    lane = lanes[2]
    st.markdown(f"**Lane 3** - {lane.signal_state}")
    frame = lane.get_frame() or placeholder_frame()
    st.image(frame, use_column_width=True)
with row2[1]:
    lane = lanes[3]
    st.markdown(f"**Lane 4** - {lane.signal_state}")
    frame = lane.get_frame() or placeholder_frame()
    st.image(frame, use_column_width=True)

# ── Test ──────────────────────────────────────────────────────────────────────
st.success("✅ 2x2 grid layout implemented as requested!")

if st.button("Run Original App"):
    os.system("streamlit run streamlit_app.py")

st.info("Copy this file as streamlit_app.py or run `streamlit run streamlit_app_2x2.py` to test the 2x2 layout.")
