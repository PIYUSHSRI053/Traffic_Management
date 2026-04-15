# 🚦 AI Smart Traffic Control System

A professional, dark-themed Streamlit application for real-time traffic monitoring and adaptive signal control using YOLOv8 object detection.

---

## ✨ Features

- **Realistic SVG Traffic Lights** — Red/Yellow/Green with glow effects
- **Video Pause/Play Logic** — Only the GREEN lane's video plays; other lanes are frozen
- **4-Lane Video Upload** — Select your own MP4/AVI/MOV/MKV files per lane
- **Adaptive Signal Timing** — Green time scales with detected vehicle density
- **Live YOLO Detection** — Cars, motorcycles, buses, trucks (YOLOv8n)
- **Accident Detection** — Flags lanes with high vehicle density
- **Premium Dark UI** — Rajdhani + Share Tech Mono fonts, glow effects, animated alerts
- **Rich Dashboard** — Trend chart, stacked bar, donut, heatmap, gauge
- **Evaluation Tab** — Metrics table + confusion matrix

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the app
```bash
streamlit run streamlit_app.py
```

### 3. Load videos
- In the sidebar, upload MP4/AVI/MOV/MKV files for each lane (Lane 1–4)
- Click **▶ Load Videos**
- The system starts cycling through lanes automatically

---

## 📁 Project Structure

```
traffic_system/
├── streamlit_app.py    # Main application + UI
├── lane.py             # Lane class (video processing, YOLO, play/pause)
├── sort.py             # SORT multi-object tracker
├── dashboard.py        # Plotly charts
├── evaluator.py        # Metrics & confusion matrix
├── config.py           # Constants (timing, classes, thresholds)
├── utils.py            # Frame conversion utilities
└── requirements.txt
```

---

## ⚙️ Signal Timing Logic

| Signal | Duration |
|--------|----------|
| GREEN  | `5s + (vehicle_count × 0.6s)`, capped at 30s |
| YELLOW | 2 seconds (fixed) |
| RED    | While other lanes cycle |

---

## 🎛️ Manual Controls

| Button | Action |
|--------|--------|
| ⏭ Next Lane | Immediately skip to next lane |
| 🔴 All Red | Force all signals to RED |
| ▶ Load Videos | Load uploaded video files |

---

## 📝 Notes

- YOLOv8n model (`yolov8n.pt`) is downloaded automatically on first run via Ultralytics
- If no model is available, the app runs in **Demo Mode** (video plays without detection)
- Videos loop automatically when they reach the end
