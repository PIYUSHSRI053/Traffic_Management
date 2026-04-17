from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw

try:
    import cv2 as _cv2
except Exception as exc:
    _cv2 = None
    CV2_IMPORT_ERROR = exc
else:
    CV2_IMPORT_ERROR = None

cv2 = _cv2


def has_cv2() -> bool:
    return cv2 is not None


def cv2_error_message() -> str:
    if CV2_IMPORT_ERROR is None:
        return ""
    return f"{type(CV2_IMPORT_ERROR).__name__}: {CV2_IMPORT_ERROR}"


def create_placeholder_frame(
    title: str = "NO VIDEO",
    subtitle: str = "Upload a video file",
    width: int = 480,
    height: int = 320,
) -> np.ndarray:
    image = Image.new("RGB", (width, height), (10, 14, 26))
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle(
        [(32, 40), (width - 32, height - 40)],
        radius=18,
        fill=(13, 20, 34),
        outline=(30, 48, 80),
        width=2,
    )
    draw.rounded_rectangle(
        [(56, 64), (width - 56, 110)],
        radius=10,
        fill=(9, 30, 54),
    )
    draw.text((width // 2, 86), title, fill=(0, 210, 255), anchor="mm")
    draw.text((width // 2, 160), subtitle, fill=(126, 152, 188), anchor="mm")
    draw.text(
        (width // 2, 214),
        "OpenCV is required for video playback and detection.",
        fill=(74, 96, 128),
        anchor="mm",
    )

    return np.array(image)
