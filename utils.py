import cv2
import numpy as np


def frame_to_bytes(frame):
    """Convert OpenCV frame to bytes for Streamlit display"""
    if frame is None:
        return None
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return rgb
