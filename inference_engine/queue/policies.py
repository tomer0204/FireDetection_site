from collections import deque

class DetectionQueue:
    def __init__(self, maxlen: int):
        self.buf = deque(maxlen=maxlen)

    def push(self, frame_idx: int, detections: dict):
        self.buf.append({
            "frame_idx": frame_idx,
            "detections": detections
        })

    def latest(self):
        if not self.buf:
            return None
        return self.buf[-1]

    def window(self, k: int):
        if k <= 0:
            return []
        return list(self.buf)[-k:]

    def __len__(self):
        return len(self.buf)
    
    
def count_frames_with_dets(det_window, min_score: float):
    c = 0
    for item in det_window:
        dets = item["detections"].get("detections", [])
        ok = any(d.get("score", 0.0) >= min_score for d in dets)
        if ok:
            c += 1
    return c

def temporal_decision(det_window, min_score: float, require_m_of_t: tuple[int, int]):
    m, t = require_m_of_t
    if t <= 0:
        return False, 0.0
    w = det_window[-t:]
    c = count_frames_with_dets(w, min_score)
    ratio = c / float(t)
    return c >= m, ratio
