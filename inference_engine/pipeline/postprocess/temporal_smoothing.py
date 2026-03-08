"""
Stage 6 — Temporal Smoothing (IOU-Based Continuity Check)
==========================================================

Validates detection persistence across frames using IOU-based tracking.
Persistent detections receive a confidence bonus; first-time detections
still pass through immediately (recall priority per SYSTEM_GOAL.md).

Mathematical Foundation
-----------------------
After IOU-based track matching (see iou_tracker.py), each detection has:
  - mrf_score   : fire probability from Stage 5
  - smoothed_score : EMA-smoothed score across matched frames
  - persistence : number of consecutive matched frames (hit count)

Final score with persistence bonus (Bayesian prior update):

    final_score = smoothed_score + β · min(hits / H_max, 1.0)

where:
  β     = persistence_bonus (default 0.15)
  H_max = max_hits_saturate (default 3) — saturation point for bonus

This rewards detections that persist across multiple frames while
ensuring first-time detections (hits=1) still receive:
    final_score = mrf_score + β · (1/3) ≈ mrf_score + 0.05

Since min_mrf_score = 0.15 and min_final_score = 0.10, first-time
detections with any fire signal above threshold pass through with zero
frame delay — critical for recall in safety-critical environments.

Latency
-------
O(1) per detection after tracker update.  Tracker update is O(n·m) where
n = detections (≤3), m = tracks (≤~10) → <0.1 ms total.
"""

import logging

logger = logging.getLogger("SMOOTH")

_DEF = {
    "persistence_bonus": 0.15,
    "max_hits_saturate": 3,
}


def temporal_smooth(detections: list, tracker, cfg: dict | None = None) -> list:
    """
    Apply IOU-based temporal smoothing to detections.

    Algorithm:
      1. Feed detections through IOUTracker.update() for track matching
      2. Compute persistence bonus per detection
      3. Set final_score = smoothed_score + persistence bonus
      4. All detections pass (no filtering here — Stage 7 handles final gate)

    Parameters
    ----------
    detections : list[dict]
        Detections with mrf_score from Stage 5.
    tracker : IOUTracker
        Persistent tracker instance (maintains state across frames).
    cfg : dict | None
        temporal_smoothing config block from live.yaml.

    Returns
    -------
    list[dict]
        Detections enriched with final_score, track_id, persistence.
    """
    if not detections:
        return []

    cfg = cfg or {}
    beta = float(cfg.get("persistence_bonus", _DEF["persistence_bonus"]))
    h_max = int(cfg.get("max_hits_saturate", _DEF["max_hits_saturate"]))
    h_max = max(1, h_max)

    # Step 1: IOU-based track matching + EMA score update
    tracked = tracker.update(detections)

    # Step 2–3: Apply persistence bonus
    for det in tracked:
        smoothed = float(det.get("smoothed_score", det.get("mrf_score", 0.0)))
        hits = int(det.get("persistence", 1))

        # Persistence bonus: scales linearly up to β at h_max hits
        bonus = beta * min(hits / float(h_max), 1.0)
        final = min(1.0, smoothed + bonus)

        det["final_score"] = round(final, 4)

    return tracked
