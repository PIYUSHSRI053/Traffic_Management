import queue
import threading
import time

import numpy as np

from config import *
from sort import Sort, iou
from vision_utils import create_placeholder_frame, cv2


class Lane:
    def __init__(self, model, position, lane_id=0):
        self.model = model
        self.tracker = Sort(max_age=2, min_hits=1, iou_threshold=0.25)
        self.cap = None
        self.running = False          # Only True when signal is GREEN
        self.position = position
        self.signal_state = "RED"
        self.lane_id = lane_id
        self.video_path = None
        self.load_error = None

        self.counts = self._empty_counts()
        self.accident = False

        self.last_frame = None        # Last frame (RGB numpy array)
        self.frame_count = 0
        self.track_labels = {}

        # Threading
        self.frame_queue = queue.Queue(maxsize=2)
        self.processing_thread = None
        self.stop_thread = threading.Event()

        # History for charts
        self.count_history = []

    @staticmethod
    def _empty_counts():
        return {"car": 0, "motorcycle": 0, "bus": 0, "truck": 0}

    @staticmethod
    def _vehicle_color(label):
        return {
            "car": (0, 200, 255),
            "motorcycle": (255, 165, 0),
            "bus": (0, 255, 100),
            "truck": (255, 50, 50),
        }.get(label, (0, 255, 0))

    def _reset_tracking_state(self):
        self.tracker = Sort(max_age=2, min_hits=1, iou_threshold=0.25)
        self.track_labels = {}
        self.counts = self._empty_counts()
        self.accident = False
        self.frame_count = 0
        self.count_history = []

        while not self.frame_queue.empty():
            try:
                self.frame_queue.get_nowait()
            except queue.Empty:
                break

    def _collect_detections(self, frame):
        if not self.model:
            return []

        results = self.model(frame, conf=CONF_THRESH, verbose=False)[0]
        detections = []

        if results.boxes is None:
            return detections

        for box in results.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            if conf < CONF_THRESH or cls_id not in ALLOWED_CLASSES:
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            if x2 <= x1 or y2 <= y1:
                continue

            detections.append({
                "bbox": np.array([x1, y1, x2, y2], dtype=float),
                "label": ALLOWED_CLASSES[cls_id],
                "conf": conf,
            })

        return detections

    @staticmethod
    def _match_track_to_detection(track_bbox, detections, used_detection_ids):
        best_idx = None
        best_score = 0.0

        for idx, detection in enumerate(detections):
            if idx in used_detection_ids:
                continue

            score = iou(track_bbox, detection["bbox"])
            if score > best_score:
                best_score = score
                best_idx = idx

        if best_idx is None or best_score < 0.1:
            return None

        return best_idx

    def set_signal(self, signal):
        """Set traffic signal state (GREEN/RED/YELLOW)"""
        self.signal_state = signal
        self.running = (signal == "GREEN")

    def load_video(self, file_path):
        """Load video from file path"""
        if cv2 is None:
            self.load_error = (
                "OpenCV is unavailable in this deployment. "
                "Keep opencv-python-headless in requirements.txt and "
                "install libgl1 plus libglib2.0-0 in packages.txt."
            )
            self.last_frame = create_placeholder_frame(
                "OpenCV Missing",
                "Cloud video features are disabled",
            )
            return False

        self.video_path = file_path
        if self.cap:
            self.cap.release()
        self.cap = cv2.VideoCapture(file_path)
        if not self.cap or not self.cap.isOpened():
            self.load_error = "Unable to open the uploaded video file."
            self.last_frame = create_placeholder_frame(
                "Video Error",
                "Could not open uploaded video",
            )
            return False

        self.load_error = None
        self.last_frame = None
        self._reset_tracking_state()
        self.start_processing()
        return True

    def load_uploaded_video(self, uploaded_file):
        """Load video from Streamlit uploaded file by saving to temp path"""
        import tempfile, os
        suffix = os.path.splitext(uploaded_file.name)[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name
        return self.load_video(tmp_path)

    def start_processing(self):
        """Start video processing thread"""
        if self.processing_thread is None or not self.processing_thread.is_alive():
            self.stop_thread.clear()
            self.processing_thread = threading.Thread(target=self._process_loop, daemon=True)
            self.processing_thread.start()

    def _process_loop(self):
        """Background thread for video processing"""
        while not self.stop_thread.is_set():
            try:
                frame = self.process()
                if frame is not None:
                    # Keep only latest frame
                    try:
                        if self.frame_queue.full():
                            try:
                                self.frame_queue.get_nowait()
                            except queue.Empty:
                                pass
                        self.frame_queue.put_nowait(frame)
                    except queue.Full:
                        pass
                # If RED/YELLOW, sleep longer (video paused)
                if self.running:
                    time.sleep(0.033)
                else:
                    time.sleep(0.2)
            except Exception as e:
                print(f"Lane {self.lane_id} processing error: {e}")
                time.sleep(0.5)

    def process(self):
        """Process single frame — advances only when GREEN (running=True)"""
        if cv2 is None:
            if self.last_frame is None:
                self.last_frame = create_placeholder_frame(
                    "OpenCV Missing",
                    "Video features are unavailable",
                )
            return self.last_frame

        if not self.cap or not self.cap.isOpened():
            return self.last_frame  # Return frozen last frame

        if not self.running:
            # Video is paused — return the last frame without advancing
            return self.last_frame

        ret, frame = self.cap.read()
        if not ret:
            # Loop video
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()
            if not ret:
                return self.last_frame

        # Resize for performance
        frame = cv2.resize(frame, (480, 320))
        self.frame_count += 1

        if self.model:
            detections = self._collect_detections(frame)
            detection_boxes = [detection["bbox"] for detection in detections]
            tracked_objects = self.tracker.update(detection_boxes)

            counts = self._empty_counts()
            used_detection_ids = set()

            for tracked_object in tracked_objects:
                track_bbox = tracked_object[:4]
                track_id = int(tracked_object[4])

                detection_idx = self._match_track_to_detection(track_bbox, detections, used_detection_ids)
                if detection_idx is not None:
                    used_detection_ids.add(detection_idx)
                    label = detections[detection_idx]["label"]
                    conf = detections[detection_idx]["conf"]
                    self.track_labels[track_id] = label
                else:
                    label = self.track_labels.get(track_id)
                    conf = None

                if not label:
                    continue

                counts[label] += 1

                x1, y1, x2, y2 = map(int, track_bbox)
                color = self._vehicle_color(label)
                text = f"{label} #{track_id}"
                if conf is not None:
                    text = f"{text} {conf:.2f}"

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(
                    frame, text,
                    (x1, max(20, y1 - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2
                )

            active_track_ids = {track.id for track in self.tracker.tracks}
            self.track_labels = {
                track_id: label
                for track_id, label in self.track_labels.items()
                if track_id in active_track_ids
            }
            self.counts = counts
        else:
            self.counts = self._empty_counts()

        total = sum(self.counts.values())
        self.accident = total > 10

        self.count_history.append(total)
        if len(self.count_history) > 60:
            self.count_history = self.count_history[-60:]

        # Draw signal overlay
        sig_colors = {"GREEN": (0, 220, 80), "RED": (220, 30, 30), "YELLOW": (255, 190, 0)}
        sig_color = sig_colors.get(self.signal_state, (150, 150, 150))
        cv2.putText(
            frame, self.signal_state,
            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, sig_color, 3
        )

        # Convert BGR -> RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.last_frame = frame_rgb
        return frame_rgb

    def get_frame(self):
        """Get latest processed frame (RGB numpy array)"""
        try:
            return self.frame_queue.get_nowait()
        except queue.Empty:
            return self.last_frame

    def stop(self):
        self.stop_thread.set()
        self.running = False
        if self.cap:
            self.cap.release()
