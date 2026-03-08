from collections import deque

class FrameQueue:
    def __init__(self, maxlen: int):
        self.q = deque(maxlen=maxlen)

    def push(self, frame_idx: int, frame_bgr, meta: dict):
        self.q.append({"frame_id": frame_idx, "frame": frame_bgr, "meta": meta})

    def latest(self):
        if not self.q:
            return None
        return self.q[-1]

    def window(self, k: int):
        if k <= 0:
            return []
        return list(self.q)[-k:]

    def __len__(self):
        return len(self.q)
