from collections import deque
import logging

logger = logging.getLogger("TEMPORAL")


class TemporalFilter:
    def __init__(self, window_size: int = 3, min_score: float = 0.20):
        self.window_size = max(1, window_size)
        self.min_score = min_score
        self._buf = deque(maxlen=self.window_size)

    def push(self, frame_idx: int, det_list: list):
        self._buf.append({"frame_idx": frame_idx, "detections": det_list})

    def evaluate(self):
        if not self._buf:
            return False, []

        frames_with_fire = 0
        for item in self._buf:
            dets = item["detections"]
            if any(d.get("score", 0.0) >= self.min_score for d in dets):
                frames_with_fire += 1

        confirmed = frames_with_fire >= 1

        latest = self._buf[-1]["detections"] if confirmed else []

        return confirmed, latest
