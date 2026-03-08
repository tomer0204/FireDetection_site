import cv2
import numpy as np

def _clamp_roi(x1, y1, x2, y2, w, h):
    x1 = max(0, min(int(x1), w - 1))
    y1 = max(0, min(int(y1), h - 1))
    x2 = max(0, min(int(x2), w - 1))
    y2 = max(0, min(int(y2), h - 1))
    if x2 <= x1 or y2 <= y1:
        return None
    return x1, y1, x2, y2

def ycrcb_fire_gate(frame_bgr, cfg: dict):
    h, w = frame_bgr.shape[:2]

    ycrcb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2YCrCb)
    y = ycrcb[:, :, 0].astype(np.int16)
    cr = ycrcb[:, :, 1].astype(np.int16)
    cb = ycrcb[:, :, 2].astype(np.int16)

    thr = cfg.get("thresholds", {})
    y_min = int(thr.get("y_min", 120))
    cr_min = int(thr.get("cr_min", 150))
    cb_max = int(thr.get("cb_max", 130))
    cr_gt_cb_margin = int(thr.get("cr_gt_cb_margin", 10))

    mask = (y >= y_min) & (cr >= cr_min) & (cb <= cb_max) & ((cr - cb) >= cr_gt_cb_margin)
    mask = mask.astype(np.uint8) * 255

    morph = cfg.get("morph", {})
    k_open = int(morph.get("open", 3))
    k_close = int(morph.get("close", 7))

    if k_open > 0:
        ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k_open, k_open))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, ker)
    if k_close > 0:
        ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k_close, k_close))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, ker)

    fire_pixels = int(np.count_nonzero(mask))
    ratio = fire_pixels / float(mask.size)

    decision = cfg.get("decision", {})
    min_ratio = float(decision.get("min_ratio", 0.001))
    is_suspicious = ratio >= min_ratio

    comps_cfg = cfg.get("components", {})
    min_area = int(comps_cfg.get("min_area", 250))
    max_rois = int(comps_cfg.get("max_rois", 3))
    pad = int(comps_cfg.get("pad", 10))

    rois = []
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    comps = []
    for i in range(1, num_labels):
        x, y0, ww, hh, area = stats[i]
        if area < min_area:
            continue
        comps.append((area, x, y0, x + ww, y0 + hh))

    comps.sort(key=lambda t: t[0], reverse=True)

    for area, x1, y1, x2, y2 in comps[:max_rois]:
        x1 -= pad
        y1 -= pad
        x2 += pad
        y2 += pad

        clamped = _clamp_roi(x1, y1, x2, y2, w, h)
        if clamped is None:
            continue

        x1, y1, x2, y2 = clamped
        rois.append({
            "x1": x1, "y1": y1, "x2": x2, "y2": y2,
            "score": float(area) / float(w * h)
        })

    return is_suspicious, float(ratio), rois
