import cv2
import numpy as np
import logging

logger = logging.getLogger("FEATURES")


def _clamp_roi(x1, y1, x2, y2, h, w):
    x1 = max(0, int(x1))
    y1 = max(0, int(y1))
    x2 = min(w, int(x2))
    y2 = min(h, int(y2))
    return x1, y1, x2, y2


def _color_features(roi_ycrcb):
    if roi_ycrcb.size == 0:
        return {"y_mean": 0, "cr_mean": 0, "cb_mean": 0, "y_std": 0, "cr_std": 0, "cb_std": 0}
    channels = cv2.split(roi_ycrcb)
    names = ["y", "cr", "cb"]
    feat = {}
    for name, ch in zip(names, channels):
        feat[f"{name}_mean"] = float(np.mean(ch))
        feat[f"{name}_std"] = float(np.std(ch))
    return feat


def _flicker_intensity(roi_gray, prev_roi_gray):
    if roi_gray.size == 0 or prev_roi_gray is None or prev_roi_gray.size == 0:
        return 0.0
    if roi_gray.shape != prev_roi_gray.shape:
        prev_roi_gray = cv2.resize(prev_roi_gray, (roi_gray.shape[1], roi_gray.shape[0]))
    diff = cv2.absdiff(roi_gray, prev_roi_gray)
    return float(np.mean(diff))


def _motion_features(roi_gray, prev_roi_gray):
    if roi_gray.size == 0 or prev_roi_gray is None or prev_roi_gray.size == 0:
        return {"flow_mag": 0.0, "divergence": 0.0}
    if roi_gray.shape != prev_roi_gray.shape:
        prev_roi_gray = cv2.resize(prev_roi_gray, (roi_gray.shape[1], roi_gray.shape[0]))
    if roi_gray.shape[0] < 5 or roi_gray.shape[1] < 5:
        return {"flow_mag": 0.0, "divergence": 0.0}
    flow = cv2.calcOpticalFlowFarneback(
        prev_roi_gray, roi_gray, None,
        pyr_scale=0.5, levels=2, winsize=11,
        iterations=2, poly_n=5, poly_sigma=1.1, flags=0
    )
    fx, fy = flow[..., 0], flow[..., 1]
    mag = np.sqrt(fx ** 2 + fy ** 2)
    # Divergence: d(fx)/dx + d(fy)/dy — positive = expansion (fire-like)
    dfx_dx = np.gradient(fx, axis=1)
    dfy_dy = np.gradient(fy, axis=0)
    div = dfx_dx + dfy_dy
    return {"flow_mag": float(np.mean(mag)), "divergence": float(np.mean(div))}


def extract_roi_features(frame_bgr, detections, prev_frame_bgr=None):
    if not detections:
        return detections

    h, w = frame_bgr.shape[:2]
    frame_ycrcb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2YCrCb)
    frame_gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)

    prev_gray = None
    if prev_frame_bgr is not None:
        prev_gray = cv2.cvtColor(prev_frame_bgr, cv2.COLOR_BGR2GRAY)

    for det in detections:
        x1, y1, x2, y2 = _clamp_roi(det["x1"], det["y1"], det["x2"], det["y2"], h, w)
        if x2 <= x1 or y2 <= y1:
            det["features"] = {}
            continue

        roi_ycrcb = frame_ycrcb[y1:y2, x1:x2]
        roi_gray = frame_gray[y1:y2, x1:x2]

        prev_roi_gray = None
        if prev_gray is not None:
            prev_roi_gray = prev_gray[y1:y2, x1:x2]

        color = _color_features(roi_ycrcb)
        flicker = _flicker_intensity(roi_gray, prev_roi_gray)
        motion = _motion_features(roi_gray, prev_roi_gray)

        det["features"] = {
            **color,
            "flicker": flicker,
            **motion,
        }

    return detections
