"""
Stage 7 — Final Bounding Box Rendering (Decision Gate + Output Formatting)
===========================================================================

Last pipeline stage before emitting detections to the frontend.  Applies
Non-Maximum Suppression (NMS), bounding-box refinement, minimum-score
filtering, and output formatting.

Non-Maximum Suppression (NMS)
-----------------------------
Greedy NMS removes duplicate overlapping detections:

    1. Sort detections by final_score in descending order
    2. For each detection d (highest score first):
       a. Add d to the output set
       b. Remove all remaining detections d' where IOU(d, d') > τ_nms
    3. Return the surviving set

Complexity: O(n² · log n) for sort + pairwise IOU.  With n ≤ 3, this is
effectively O(1).

Bounding Box Refinement
-----------------------
Each surviving bbox is expanded by a small margin m and clamped to frame
boundaries:

    x1' = max(0,   x1 − m)
    y1' = max(0,   y1 − m)
    x2' = min(W−1, x2 + m)
    y2' = min(H−1, y2 + m)

This accounts for slight CNN localisation errors and ensures the full
fire region is captured.

Minimum Score Gate
------------------
min_final_score defaults to 0.10 — very permissive.  Per SYSTEM_GOAL.md,
missed detections are more harmful than false alarms.  The threshold only
filters obvious non-fire artefacts that survived earlier stages.

Minimum Dimension Filter
-------------------------
Detections with width < 4px or height < 4px are removed as they are too
small to meaningfully represent fire and would cause rendering artefacts.

Output Format
-------------
Each detection emitted to frontend must have:
  - x1, y1, x2, y2 : float — bounding box coordinates in image space
  - score : float           — final pipeline confidence (= final_score)
  - label : str             — always "fire"
"""

import logging

from pipeline.postprocess.output_format import refine_bbox

logger = logging.getLogger("FINAL")

_DEF = {
    "min_final_score": 0.10,
    "bbox_margin": 5,
    "nms_iou_threshold": 0.5,
    "min_bbox_dim": 4,
}


def _compute_iou(a: dict, b: dict) -> float:
    """Axis-aligned IOU between two detection dicts."""
    ax1, ay1 = float(a["x1"]), float(a["y1"])
    ax2, ay2 = float(a["x2"]), float(a["y2"])
    bx1, by1 = float(b["x1"]), float(b["y1"])
    bx2, by2 = float(b["x2"]), float(b["y2"])

    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)

    inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    union = area_a + area_b - inter

    return inter / union if union > 0 else 0.0


def _nms(detections: list, iou_threshold: float) -> list:
    """
    Greedy Non-Maximum Suppression.

    Algorithm:
      1. Sort by final_score descending
      2. Pick highest-scoring detection, suppress all with IOU > threshold
      3. Repeat for remaining detections

    Parameters
    ----------
    detections : list[dict]
        Must have ``final_score``, ``x1``, ``y1``, ``x2``, ``y2``.
    iou_threshold : float
        Overlap threshold above which lower-scored detections are suppressed.

    Returns
    -------
    list[dict]
        Surviving detections after NMS.
    """
    if len(detections) <= 1:
        return list(detections)

    sorted_dets = sorted(detections, key=lambda d: d.get("final_score", 0), reverse=True)
    keep = []

    while sorted_dets:
        best = sorted_dets.pop(0)
        keep.append(best)
        sorted_dets = [
            d for d in sorted_dets
            if _compute_iou(best, d) < iou_threshold
        ]

    return keep


def final_decision(detections: list, frame_shape: tuple,
                   cfg: dict | None = None) -> list:
    """
    Stage 7: Final rendering gate.

    Algorithm:
      1. Filter by min_final_score (0.10, recall-priority)
      2. NMS to remove duplicate overlapping detections
      3. Refine bboxes with margin padding + frame clamping
      4. Validate minimum bbox dimensions (≥4px width and height)
      5. Format output for frontend: x1, y1, x2, y2, score, label

    Parameters
    ----------
    detections : list[dict]
        Detections with final_score from Stage 6.
    frame_shape : tuple
        (H, W, C) or (H, W) of the current frame.
    cfg : dict | None
        final_rendering config block from live.yaml.

    Returns
    -------
    list[dict]
        Validated detections ready for Socket.IO emission to frontend.
    """
    if not detections:
        return []

    cfg = cfg or {}
    min_score = float(cfg.get("min_final_score", _DEF["min_final_score"]))
    margin = int(cfg.get("bbox_margin", _DEF["bbox_margin"]))
    nms_iou = float(cfg.get("nms_iou_threshold", _DEF["nms_iou_threshold"]))
    min_dim = int(cfg.get("min_bbox_dim", _DEF["min_bbox_dim"]))

    h, w = frame_shape[:2]

    # Step 1: Score filter
    scored = [d for d in detections if d.get("final_score", 0) >= min_score]
    if not scored:
        return []

    # Step 2: NMS
    nms_result = _nms(scored, nms_iou)

    # Steps 3–5: Refine + validate + format
    output = []
    for det in nms_result:
        bbox = (float(det["x1"]), float(det["y1"]),
                float(det["x2"]), float(det["y2"]))

        # Refine: add margin, clamp to frame
        x1, y1, x2, y2 = refine_bbox(bbox, frame_shape, margin=margin)

        # Validate minimum dimensions
        if (x2 - x1) < min_dim or (y2 - y1) < min_dim:
            continue

        # Format for frontend
        output.append({
            "x1": round(float(x1), 2),
            "y1": round(float(y1), 2),
            "x2": round(float(x2), 2),
            "y2": round(float(y2), 2),
            "score": round(float(det.get("final_score", 0)), 4),
            "label": "fire",
        })

    return output
