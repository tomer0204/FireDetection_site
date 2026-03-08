import cv2
from pipeline.orchestrator import PipelineContext, process_frame

RUST_URL = "http://127.0.0.1:8088"

color_cfg = {
    "thresholds": {
        "y_min": 120,
        "cr_min": 150,
        "cb_max": 130,
        "cr_gt_cb_margin": 10
    },
    "decision": {
        "min_ratio": 0.001
    },
    "components": {
        "min_area": 250,
        "max_rois": 3,
        "pad": 10
    }
}

ctx = PipelineContext(RUST_URL)

cap = cv2.VideoCapture("test.mp4")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    decision = process_frame(frame, ctx, color_cfg)

    if decision:
        print("🔥 FIRE DETECTED:", decision)

cap.release()
