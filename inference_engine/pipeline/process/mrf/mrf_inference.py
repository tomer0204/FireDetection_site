"""
Stage 5 — MRF Pixel-Level Classification
=========================================

Markov Random Field (MRF) based fire classification on CNN ROIs.

Mathematical Foundation
-----------------------
An MRF models the joint probability of labels L = {fire, non-fire} over a set
of ROIs by minimising an energy function:

    E(L) = Σᵢ ψᵤ(lᵢ, fᵢ) + λ · Σ_{(i,j)∈N} ψₚ(lᵢ, lⱼ)

where:
  ψᵤ  = Unary potential   — cost of label lᵢ given feature vector fᵢ
  ψₚ  = Pairwise potential — cost of assigning different labels to neighbours
  N   = Neighbourhood (ROIs with spatial proximity)
  λ   = Smoothness weight  — balances data fidelity vs spatial coherence

Unary Potential (fire likelihood from Stage 4 features)
-------------------------------------------------------
Three cues are combined via logistic sigmoid σ(x) = 1 / (1 + e^{-x}):

  P_color   = σ((cr_mean - τ_cr) / s_cr) · σ((τ_cb - cb_mean) / s_cb)
              · σ((y_mean - τ_y) / s_y)

  P_flicker = min(1, flicker / flicker_norm)

  P_motion  = σ(divergence / div_scale) · min(1, flow_mag / mag_norm)

  fire_likelihood = w_c·P_color + w_f·P_flicker + w_m·P_motion

  ψᵤ(fire)     = −log(fire_likelihood + ε)
  ψᵤ(non-fire) = −log(1 − fire_likelihood + ε)

Pairwise Potential (Potts model with distance weighting)
--------------------------------------------------------
  ψₚ(lᵢ, lⱼ) = exp(−d²(i,j) / (2σ²_spatial)) · [lᵢ ≠ lⱼ]

d(i,j) = Euclidean distance between ROI centres.

Optimisation — Single-Pass Mean-Field Approximation
----------------------------------------------------
With ≤ 3 ROIs (capped by color gate max_rois), a single mean-field pass is
sufficient and avoids iterative loopy belief propagation:

  For each ROI i:
    message = Σⱼ ψₚ(fire, lⱼ) · Q(lⱼ = fire)
    Q(lᵢ = fire)  ∝ exp(−ψᵤ(fire))  · exp(−λ · message)
    Q(lᵢ = ¬fire) ∝ exp(−ψᵤ(¬fire)) · exp(+λ · message)
    mrf_score = Q(fire) / (Q(fire) + Q(¬fire))

Complexity: O(n²) where n ≤ 3 → <0.1 ms.

Recall Priority
---------------
min_mrf_score defaults to 0.15 — very permissive.  Per SYSTEM_GOAL.md we
must never miss a real fire event; precision is secondary.
"""

import math
import logging

logger = logging.getLogger("MRF")

# ── Defaults ────────────────────────────────────────────────────────────────
_DEF = {
    "weights": {"color": 0.4, "flicker": 0.3, "motion": 0.3},
    "fire_thresholds": {"cr_mean_min": 140, "cb_mean_max": 140, "y_mean_min": 100},
    "sigmoid_scales": {"cr": 20.0, "cb": 20.0, "y": 30.0},
    "flicker_norm": 30.0,
    "flow_mag_norm": 5.0,
    "div_scale": 2.0,
    "lambda_smooth": 0.3,
    "spatial_sigma": 100.0,
    "min_mrf_score": 0.15,
}

_EPS = 1e-8


def _sigmoid(x: float) -> float:
    """Logistic sigmoid:  σ(x) = 1 / (1 + e^{-x})"""
    if x >= 0:
        return 1.0 / (1.0 + math.exp(-x))
    # Numerically stable for large negative x
    ex = math.exp(x)
    return ex / (1.0 + ex)


def _fire_likelihood(feat: dict, cfg: dict) -> float:
    """
    Compute P(fire | features) from Stage 4 feature vector.

    Returns a value in (0, 1).
    """
    w = cfg.get("weights", _DEF["weights"])
    th = cfg.get("fire_thresholds", _DEF["fire_thresholds"])
    sc = cfg.get("sigmoid_scales", _DEF["sigmoid_scales"])

    cr_mean = feat.get("cr_mean", 0.0)
    cb_mean = feat.get("cb_mean", 0.0)
    y_mean = feat.get("y_mean", 0.0)
    flicker = feat.get("flicker", 0.0)
    flow_mag = feat.get("flow_mag", 0.0)
    divergence = feat.get("divergence", 0.0)

    # ── Colour cue ──────────────────────────────────────────────────────
    # Fire has high Cr, low Cb, moderate-to-high Y in YCrCb space.
    # Each sigmoid saturates to 1 when the feature exceeds the threshold.
    p_cr = _sigmoid((cr_mean - th.get("cr_mean_min", 140)) / max(sc.get("cr", 20), 0.01))
    p_cb = _sigmoid((th.get("cb_mean_max", 140) - cb_mean) / max(sc.get("cb", 20), 0.01))
    p_y = _sigmoid((y_mean - th.get("y_mean_min", 100)) / max(sc.get("y", 30), 0.01))
    p_color = p_cr * p_cb * p_y  # product ∈ (0, 1)

    # ── Flicker cue ─────────────────────────────────────────────────────
    # Fire flickers → nonzero frame-to-frame intensity difference.
    fnorm = cfg.get("flicker_norm", _DEF["flicker_norm"])
    p_flicker = min(1.0, max(0.0, flicker) / max(fnorm, 0.01))

    # ── Motion cue ──────────────────────────────────────────────────────
    # Positive divergence = expansion (fire grows outward).
    # High flow magnitude = motion in the ROI.
    ds = cfg.get("div_scale", _DEF["div_scale"])
    mn = cfg.get("flow_mag_norm", _DEF["flow_mag_norm"])
    p_div = _sigmoid(divergence / max(ds, 0.01))
    p_mag = min(1.0, max(0.0, flow_mag) / max(mn, 0.01))
    p_motion = p_div * p_mag

    # ── Weighted combination ────────────────────────────────────────────
    wc = float(w.get("color", 0.4))
    wf = float(w.get("flicker", 0.3))
    wm = float(w.get("motion", 0.3))
    total_w = wc + wf + wm
    if total_w <= 0:
        total_w = 1.0

    likelihood = (wc * p_color + wf * p_flicker + wm * p_motion) / total_w
    return max(_EPS, min(1.0 - _EPS, likelihood))


def _roi_center(det: dict) -> tuple:
    """Return (cx, cy) of the bounding box."""
    cx = (float(det.get("x1", 0)) + float(det.get("x2", 0))) / 2.0
    cy = (float(det.get("y1", 0)) + float(det.get("y2", 0))) / 2.0
    return cx, cy


def _euclidean(c1: tuple, c2: tuple) -> float:
    return math.sqrt((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2)


def mrf_classify(detections: list, frame_shape: tuple, cfg: dict | None = None) -> list:
    """
    MRF-based fire classification on CNN ROIs.

    Algorithm:
      1. Compute unary potentials from Stage 4 features
      2. Build spatial neighbourhood graph from ROI centres
      3. Single-pass mean-field update for label probabilities
      4. Filter by min_mrf_score (recall-priority: default 0.15)

    Parameters
    ----------
    detections : list[dict]
        Detections enriched with ``"features"`` dict from Stage 4.
    frame_shape : tuple
        (H, W, C) of the current frame (used for spatial scaling).
    cfg : dict | None
        MRF config block from live.yaml.

    Returns
    -------
    list[dict]
        Detections that survive MRF filtering, each with ``"mrf_score"`` added.
    """
    if not detections:
        return []

    cfg = cfg or {}
    lam = float(cfg.get("lambda_smooth", _DEF["lambda_smooth"]))
    sigma = float(cfg.get("spatial_sigma", _DEF["spatial_sigma"]))
    min_score = float(cfg.get("min_mrf_score", _DEF["min_mrf_score"]))

    n = len(detections)

    # ── Step 1: Unary potentials ────────────────────────────────────────
    likelihoods = []
    centres = []
    for det in detections:
        feat = det.get("features", {})
        fl = _fire_likelihood(feat, cfg)
        likelihoods.append(fl)
        centres.append(_roi_center(det))

    # ── Step 2: Pairwise weights (Potts kernel) ────────────────────────
    # W[i][j] = exp(−d²/(2σ²))  for i≠j, 0 for i==j
    pairwise = [[0.0] * n for _ in range(n)]
    sigma_sq2 = 2.0 * sigma * sigma if sigma > 0 else 1.0
    for i in range(n):
        for j in range(i + 1, n):
            d = _euclidean(centres[i], centres[j])
            w = math.exp(-(d * d) / sigma_sq2)
            pairwise[i][j] = w
            pairwise[j][i] = w

    # ── Step 3: Mean-field update (single pass) ────────────────────────
    # Q(fire_i) ∝ exp(−ψᵤ(fire)) · exp(−λ · Σⱼ W[i][j] · Q(fire_j))
    # Initialise Q from unary likelihoods
    q_fire = list(likelihoods)

    for i in range(n):
        # Message from neighbours
        msg = 0.0
        for j in range(n):
            if j != i:
                # Pairwise penalty for disagreement, weighted by neighbour confidence
                msg += pairwise[i][j] * q_fire[j]

        # Unary energy
        psi_fire = -math.log(likelihoods[i] + _EPS)
        psi_nofire = -math.log(1.0 - likelihoods[i] + _EPS)

        # Mean-field update with spatial smoothing
        # Neighbour agreement boosts fire probability (msg > 0 when neighbours are fire-like)
        log_q_fire = -psi_fire + lam * msg
        log_q_nofire = -psi_nofire - lam * msg

        # Normalise via softmax
        max_log = max(log_q_fire, log_q_nofire)
        exp_fire = math.exp(log_q_fire - max_log)
        exp_nofire = math.exp(log_q_nofire - max_log)
        q_fire[i] = exp_fire / (exp_fire + exp_nofire)

    # ── Step 4: Attach scores and filter ────────────────────────────────
    result = []
    for i, det in enumerate(detections):
        score = q_fire[i]
        det["mrf_score"] = round(score, 4)

        if score >= min_score:
            result.append(det)
        else:
            logger.debug(
                f"[MRF] filtered det x1={det.get('x1'):.0f} mrf_score={score:.3f} "
                f"< min={min_score}"
            )

    return result
