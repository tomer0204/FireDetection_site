"""
IOU-Based Multi-Object Tracker
================================

Provides frame-to-frame bounding-box association for Stage 6 temporal smoothing.

Mathematical Foundation
-----------------------
Intersection over Union (IOU) measures overlap between two axis-aligned boxes
A = [x1_a, y1_a, x2_a, y2_a] and B = [x1_b, y1_b, x2_b, y2_b]:

    intersection_w = max(0, min(x2_a, x2_b) − max(x1_a, x1_b))
    intersection_h = max(0, min(y2_a, y2_b) − max(y1_a, y1_b))
    intersection   = intersection_w · intersection_h
    union          = Area(A) + Area(B) − intersection
    IOU(A, B)      = intersection / union          ∈ [0, 1]

Greedy Assignment (Hungarian-lite)
----------------------------------
Given n detections and m tracks, build an n×m IOU matrix M.

    1. Find (i*, j*) = argmax M[i][j]
    2. If M[i*][j*] ≥ iou_threshold → assign det i* to track j*
    3. Remove row i* and column j* from M
    4. Repeat until no valid assignments remain
    5. Unmatched detections → create new tracks
    6. Unmatched tracks → increment age; prune if age > max_age

Design choice: greedy over Hungarian because n,m ≤ 3 (capped by color gate
max_rois).  At this scale greedy is optimal and avoids scipy dependency.
Complexity: O(n · m · min(n, m)).

Exponential Moving Average (EMA) Score Smoothing
-------------------------------------------------
Each track maintains a smoothed score updated on every match:

    s_t = α · mrf_score_t + (1 − α) · s_{t−1}

α = 0.6 by default — weights recent observations more for responsiveness in
live systems while still dampening transient noise.
"""

import logging

logger = logging.getLogger("IOU_TRACKER")


def compute_iou(box_a: dict, box_b: dict) -> float:
    """
    Standard axis-aligned IOU between two boxes represented as dicts with
    keys x1, y1, x2, y2.

    Returns
    -------
    float
        IOU value ∈ [0, 1].
    """
    ax1, ay1 = float(box_a.get("x1", 0)), float(box_a.get("y1", 0))
    ax2, ay2 = float(box_a.get("x2", 0)), float(box_a.get("y2", 0))
    bx1, by1 = float(box_b.get("x1", 0)), float(box_b.get("y1", 0))
    bx2, by2 = float(box_b.get("x2", 0)), float(box_b.get("y2", 0))

    # Intersection rectangle
    ix1 = max(ax1, bx1)
    iy1 = max(ay1, by1)
    ix2 = min(ax2, bx2)
    iy2 = min(ay2, by2)

    iw = max(0.0, ix2 - ix1)
    ih = max(0.0, iy2 - iy1)
    inter = iw * ih

    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    union = area_a + area_b - inter

    if union <= 0:
        return 0.0
    return inter / union


class IOUTracker:
    """
    Multi-object tracker using IOU-based frame-to-frame association.

    Each track stores:
      - box: dict with x1, y1, x2, y2 (updated to latest matched detection)
      - smoothed_score: EMA-smoothed fire score
      - age: frames since last match (reset to 0 on match)
      - hits: total number of matched frames
      - track_id: unique integer ID

    Parameters
    ----------
    iou_threshold : float
        Minimum IOU to consider a detection-track pair a match.
    max_age : int
        Number of unmatched frames before a track is pruned.
    ema_alpha : float
        Weight for new observation in EMA:  s = α·new + (1−α)·old.
    """

    def __init__(self, iou_threshold: float = 0.3, max_age: int = 5,
                 ema_alpha: float = 0.6):
        self.iou_threshold = iou_threshold
        self.max_age = max_age
        self.ema_alpha = ema_alpha
        self._tracks: list[dict] = []
        self._next_id: int = 1

    def update(self, detections: list) -> list:
        """
        Match current detections to existing tracks.

        Algorithm (greedy):
          1. Build IOU matrix between detections and tracks
          2. Greedily assign best-IOU pairs above threshold
          3. Update matched tracks (box, EMA score, reset age, increment hits)
          4. Create new tracks for unmatched detections
          5. Age and prune unmatched tracks

        Parameters
        ----------
        detections : list[dict]
            Current frame detections with x1, y1, x2, y2, mrf_score.

        Returns
        -------
        list[dict]
            Input detections enriched with ``track_id``, ``persistence``
            (hit count), and ``smoothed_score`` fields.
        """
        if not detections and not self._tracks:
            return []

        n_det = len(detections)
        n_trk = len(self._tracks)

        # ── Build IOU matrix ────────────────────────────────────────────
        iou_matrix = [[0.0] * n_trk for _ in range(n_det)]
        for di in range(n_det):
            for ti in range(n_trk):
                iou_matrix[di][ti] = compute_iou(detections[di], self._tracks[ti]["box"])

        # ── Greedy assignment ───────────────────────────────────────────
        matched_dets = set()
        matched_trks = set()

        for _ in range(min(n_det, n_trk)):
            best_iou = -1.0
            best_d, best_t = -1, -1

            for di in range(n_det):
                if di in matched_dets:
                    continue
                for ti in range(n_trk):
                    if ti in matched_trks:
                        continue
                    if iou_matrix[di][ti] > best_iou:
                        best_iou = iou_matrix[di][ti]
                        best_d, best_t = di, ti

            if best_iou < self.iou_threshold:
                break

            matched_dets.add(best_d)
            matched_trks.add(best_t)

            # Update track
            track = self._tracks[best_t]
            new_score = float(detections[best_d].get("mrf_score", 0.0))
            track["smoothed_score"] = (
                self.ema_alpha * new_score
                + (1.0 - self.ema_alpha) * track["smoothed_score"]
            )
            track["box"] = {
                "x1": detections[best_d]["x1"],
                "y1": detections[best_d]["y1"],
                "x2": detections[best_d]["x2"],
                "y2": detections[best_d]["y2"],
            }
            track["age"] = 0
            track["hits"] += 1

            # Enrich detection
            detections[best_d]["track_id"] = track["track_id"]
            detections[best_d]["persistence"] = track["hits"]
            detections[best_d]["smoothed_score"] = round(track["smoothed_score"], 4)

        # ── New tracks for unmatched detections ─────────────────────────
        for di in range(n_det):
            if di in matched_dets:
                continue
            tid = self._next_id
            self._next_id += 1

            init_score = float(detections[di].get("mrf_score", 0.0))
            self._tracks.append({
                "track_id": tid,
                "box": {
                    "x1": detections[di]["x1"],
                    "y1": detections[di]["y1"],
                    "x2": detections[di]["x2"],
                    "y2": detections[di]["y2"],
                },
                "smoothed_score": init_score,
                "age": 0,
                "hits": 1,
            })
            detections[di]["track_id"] = tid
            detections[di]["persistence"] = 1
            detections[di]["smoothed_score"] = round(init_score, 4)

        # ── Age and prune unmatched tracks ──────────────────────────────
        surviving = []
        for ti in range(n_trk):
            if ti in matched_trks:
                surviving.append(self._tracks[ti])
            else:
                self._tracks[ti]["age"] += 1
                if self._tracks[ti]["age"] <= self.max_age:
                    surviving.append(self._tracks[ti])

        # Keep newly created tracks too (already appended above)
        for ti in range(n_trk, len(self._tracks)):
            surviving.append(self._tracks[ti])

        self._tracks = surviving

        return detections
