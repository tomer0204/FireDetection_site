import time
import requests
import logging
from pipeline.preprocess.color_gate import ycrcb_fire_gate

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("ORCH")


def _normalize_rust_infer_url(base: str) -> str:
    base = (base or "").strip()
    if not base:
        return ""
    if base.endswith("/"):
        base = base[:-1]
    if base.endswith("/infer"):
        return base
    return f"{base}/infer"


class PipelineContext:
    def __init__(self, rust_url: str):
        self.state = "COLOR_GATE"
        self.active_rois = []
        self.rust_url = _normalize_rust_infer_url(rust_url)
        logger.info(f"[INIT] rust_url={self.rust_url}")


def call_rust_infer(frame_bgr, rust_url):
    import cv2

    rust_url = _normalize_rust_infer_url(rust_url)
    if not rust_url:
        return None

    ok, buf = cv2.imencode(".jpg", frame_bgr)
    if not ok:
        logger.error("[RUST] jpeg_encode_failed")
        return None

    t0 = time.time()
    try:
        r = requests.post(
            rust_url,
            data=buf.tobytes(),
            headers={"Content-Type": "image/jpeg"},
            timeout=2.0,
        )
        ms = (time.time() - t0) * 1000.0

        if r.status_code != 200:
            logger.error(f"[RUST] http={r.status_code} latency_ms={ms:.2f}")
            return None

        data = r.json()
        dets = []
        if isinstance(data, dict):
            dets = data.get("detections", [])
        det_count = len(dets) if isinstance(dets, list) else 0

        logger.info(f"[RUST] ok latency_ms={ms:.2f} detections={det_count}")
        return data

    except Exception as e:
        ms = (time.time() - t0) * 1000.0
        logger.error(f"[RUST] exception latency_ms={ms:.2f} err={e}")
        return None


def process_frame(frame_bgr, ctx: PipelineContext, color_cfg):
    if ctx.state == "COLOR_GATE":
        suspicious, ratio, rois = ycrcb_fire_gate(frame_bgr, color_cfg)

        logger.info(f"[COLOR_GATE] suspicious={suspicious} ratio={ratio:.6f} rois={len(rois)}")

        if not suspicious:
            return None

        ctx.active_rois = rois
        ctx.state = "YOLO"
        logger.info("[STATE] -> YOLO")
        return None

    if ctx.state == "YOLO":
        dets = call_rust_infer(frame_bgr, ctx.rust_url)

        det_list = []
        if isinstance(dets, dict):
            det_list = dets.get("detections", [])
        if not isinstance(det_list, list) or len(det_list) == 0:
            logger.info("[YOLO] no detections -> back to COLOR_GATE")
            ctx.state = "COLOR_GATE"
            return None

        ctx.active_rois = det_list
        logger.info(f"[YOLO] detections={len(ctx.active_rois)}")
        ctx.state = "FINAL"
        logger.info("[STATE] -> FINAL")
        return None

    if ctx.state == "FINAL":
        decision = {"fire": True, "detections": ctx.active_rois, "ts": time.time()}
        logger.info(f"[FINAL] FIRE CONFIRMED detections={len(ctx.active_rois)}")
        ctx.state = "COLOR_GATE"
        return decision

    ctx.state = "COLOR_GATE"
    return None
