import os
import time
import uuid
import threading
import requests
import cv2
import yaml
import logging

from ingest.stream_reader import StreamReader
from pipeline.preprocess.color_gate.ycrcb_gate import ycrcb_fire_gate
from pipeline.preprocess.color_gate.sampling_policy import should_check_color, should_run_yolo
from pipeline.process.temporal.temporal_filter import TemporalFilter
from pipeline.process.mrf.feature_extraction import extract_roi_features

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("STREAM")

_LIVE_CFG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "configs", "live.yaml")


def _normalize_rust_infer_url(base: str) -> str:
    base = (base or "").strip()
    if not base:
        return ""
    if base.endswith("/"):
        base = base[:-1]
    if base.endswith("/infer"):
        return base
    return f"{base}/infer"


class StreamManager:
    def __init__(self, cameras: dict, socketio, archive_writer=None, enable_archive=True):
        self.cameras = cameras
        self.socketio = socketio
        self.archive_writer = archive_writer
        self.enable_archive = enable_archive

        self._lock = threading.Lock()
        self._threads = {}
        self._stop_flags = {}
        self._active = {}

        self.sample_every_n = int(self._env("COLOR_SAMPLE_EVERY_N", "10"))
        self.jpeg_quality = int(self._env("JPEG_QUALITY", "85"))
        self.rust_url = _normalize_rust_infer_url(self._env("RUST_INFER_URL", ""))
        self.rust_timeout = float(self._env("RUST_TIMEOUT_SEC", "2.0"))

        self.live_cfg = self._load_live_config()

        logger.info(f"[INIT] sample_every_n={self.sample_every_n} jpeg_quality={self.jpeg_quality}")
        logger.info(f"[INIT] rust_url={self.rust_url} rust_timeout={self.rust_timeout}")
        logger.info(f"[INIT] color_gate config loaded from {_LIVE_CFG_PATH}")

    def _env(self, k, default):
        return os.getenv(k, default)

    @staticmethod
    def _load_live_config():
        try:
            with open(_LIVE_CFG_PATH, "r") as f:
                cfg = yaml.safe_load(f) or {}
            return cfg
        except FileNotFoundError:
            logger.warning(f"[INIT] {_LIVE_CFG_PATH} not found, using defaults")
            return {}

    @staticmethod
    def _rescale_detections(det_list, meta):
        if not meta or not det_list:
            return det_list
        model_w = float(meta.get("model_width", 640))
        model_h = float(meta.get("model_height", 640))
        input_w = float(meta.get("input_width", model_w))
        input_h = float(meta.get("input_height", model_h))
        if model_w <= 0 or model_h <= 0:
            return det_list
        scale_x = input_w / model_w
        scale_y = input_h / model_h
        for d in det_list:
            d["x1"] = d["x1"] * scale_x
            d["y1"] = d["y1"] * scale_y
            d["x2"] = d["x2"] * scale_x
            d["y2"] = d["y2"] * scale_y
            d["label"] = "fire"
        return det_list

    def get_state(self):
        with self._lock:
            return {"active_runs": list(self._active.keys())}

    def start(self, camera_id: int, fps: int = 10):
        camera_id = int(camera_id)
        if camera_id not in self.cameras:
            raise ValueError("Camera not found")

        run_id = uuid.uuid4().hex
        stop_flag = threading.Event()
        s3_prefix = f"cameras/{camera_id}/runs/{run_id}"

        with self._lock:
            self._stop_flags[run_id] = stop_flag
            self._active[run_id] = {
                "camera_id": camera_id,
                "fps": int(fps),
                "started_at": time.time(),
                "frame_index": 0,
                "s3_prefix": s3_prefix,
            }

        t = threading.Thread(target=self._run_loop, args=(run_id,), daemon=True)
        with self._lock:
            self._threads[run_id] = t
        t.start()

        logger.info(f"[START] camera={camera_id} run_id={run_id} fps={int(fps)} s3_prefix={s3_prefix}")

        return {"run_id": run_id, "camera_id": camera_id, "fps": int(fps), "s3_prefix": s3_prefix}

    def stop(self, run_id: str | None):
        if not run_id:
            return
        run_id = str(run_id)

        with self._lock:
            flag = self._stop_flags.get(run_id)
            t = self._threads.get(run_id)

        if flag:
            flag.set()

        if t and t is not threading.current_thread():
            t.join(timeout=5)

        with self._lock:
            self._threads.pop(run_id, None)
            self._stop_flags.pop(run_id, None)
            self._active.pop(run_id, None)

        logger.info(f"[STOP] run_id={run_id}")

    def _encode_jpeg(self, frame_bgr):
        ok, buf = cv2.imencode(".jpg", frame_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), int(self.jpeg_quality)])
        if not ok:
            logger.error("[JPEG] encode failed")
            return None
        return buf.tobytes()

    def _maybe_rust_infer(self, jpeg_bytes: bytes):
        if not self.rust_url:
            return None

        t0 = time.time()
        try:
            r = requests.post(
                self.rust_url,
                data=jpeg_bytes,
                headers={"Content-Type": "image/jpeg"},
                timeout=self.rust_timeout,
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

    def _run_loop(self, run_id: str):
        with self._lock:
            st = self._active.get(run_id)
            flag = self._stop_flags.get(run_id)

        if not st or not flag:
            return

        camera_id = int(st["camera_id"])
        fps = int(st["fps"])
        delay = 1.0 / max(1, fps)

        cfg = self.cameras[camera_id]
        reader = StreamReader(cfg["source"])

        if self.enable_archive and self.archive_writer:
            self.archive_writer.ensure_bucket()

        # Pipeline config from live.yaml
        color_cfg = self.live_cfg.get("color_gate", {})
        sampling_cfg = self.live_cfg.get("sampling", {})
        check_every_n = int(sampling_cfg.get("check_color_every_n", 3))
        cooldown_frames = int(sampling_cfg.get("yolo_cooldown_frames", 12))
        cooldown_state = {"cooldown_left": 0}

        # Stage 3: Temporal filter
        tf_cfg = self.live_cfg.get("temporal_filter", {})
        temporal_filter = TemporalFilter(
            window_size=int(tf_cfg.get("window_size", 3)),
            min_score=float(tf_cfg.get("min_score", 0.20)),
        )

        # Stage 4: Feature extraction state (previous frame)
        prev_frame = None

        last_status_emit = 0.0

        logger.info(
            f"[RUN] camera={camera_id} run_id={run_id} fps={fps} "
            f"check_color_every={check_every_n} yolo_cooldown={cooldown_frames}"
        )

        try:
            while not flag.is_set():
                item = reader.read()
                if item is None:
                    break

                frame_idx, frame = item
                jpeg = None

                # Emit frames to frontend for live display (sampled)
                do_display = frame_idx % max(1, self.sample_every_n) == 0
                if do_display:
                    jpeg = self._encode_jpeg(frame)
                    if jpeg:
                        self.socketio.emit(
                            "infer_frame",
                            {"run_id": run_id, "frame_index": frame_idx, "frame": jpeg},
                            room=f"run:{run_id}",
                        )

                # Stage 1: YCrCb color-based suspicion sampling
                if should_check_color(frame_idx, check_every_n):
                    t0 = time.time()
                    suspicious, ratio, rois = ycrcb_fire_gate(frame, color_cfg)
                    gate_ms = (time.time() - t0) * 1000.0

                    logger.info(
                        f"[COLOR_GATE] frame={frame_idx} suspicious={suspicious} "
                        f"ratio={ratio:.6f} rois={len(rois)} latency_ms={gate_ms:.1f}"
                    )

                    # Stage 2: CNN detection — only when suspicious + cooldown expired
                    if should_run_yolo(frame_idx, suspicious, cooldown_state, cooldown_frames):
                        if jpeg is None:
                            jpeg = self._encode_jpeg(frame)
                        if jpeg:
                            dets = self._maybe_rust_infer(jpeg)
                            if isinstance(dets, dict):
                                det_list = dets.get("detections", [])
                                if not isinstance(det_list, list):
                                    det_list = []
                                meta = dets.get("meta")
                                det_list = self._rescale_detections(det_list, meta)

                                # Stage 3: Temporal filtering
                                temporal_filter.push(frame_idx, det_list)
                                confirmed, confirmed_dets = temporal_filter.evaluate()

                                logger.info(
                                    f"[TEMPORAL] frame={frame_idx} "
                                    f"confirmed={confirmed} dets={len(confirmed_dets)}"
                                )

                                if confirmed and confirmed_dets:
                                    # Stage 4: Feature extraction
                                    t0_feat = time.time()
                                    enriched = extract_roi_features(
                                        frame, confirmed_dets, prev_frame
                                    )
                                    feat_ms = (time.time() - t0_feat) * 1000.0
                                    logger.info(
                                        f"[FEATURES] frame={frame_idx} "
                                        f"rois={len(enriched)} latency_ms={feat_ms:.1f}"
                                    )

                                    payload = {
                                        "run_id": run_id,
                                        "frame_index": frame_idx,
                                        "detections": enriched,
                                    }

                                    logger.info(
                                        f"[EMIT] infer_result frame={frame_idx} "
                                        f"detections={len(enriched)}"
                                    )

                                    self.socketio.emit(
                                        "infer_result", payload, room=f"run:{run_id}"
                                    )

                # Track previous frame for feature extraction
                prev_frame = frame

                # Archive sampled frames (non-fatal on failure)
                if jpeg and self.enable_archive and self.archive_writer:
                    try:
                        with self._lock:
                            s3_prefix = self._active.get(run_id, {}).get("s3_prefix")
                        if s3_prefix:
                            key = f"{s3_prefix}/frames/{frame_idx:06d}.jpg"
                            self.archive_writer.put_jpeg(key, jpeg)
                    except Exception as e:
                        logger.warning(f"[ARCHIVE] failed frame={frame_idx} err={e}")

                now = time.time()
                if now - last_status_emit > 2.0:
                    self.socketio.emit(
                        "infer_status",
                        {"run_id": run_id, "camera_id": camera_id, "frame_index": frame_idx},
                        room=f"run:{run_id}",
                    )
                    last_status_emit = now

                time.sleep(delay)

        finally:
            reader.close()
            logger.info(f"[END] run_id={run_id}")
            self.socketio.emit("infer_ended", {"run_id": run_id}, room=f"run:{run_id}")
            self.stop(run_id)
