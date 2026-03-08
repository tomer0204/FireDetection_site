from collections import deque

class RoiQueue:
    def __init__(self, maxlen: int):
        self.q = deque(maxlen=maxlen)

    def push(self, frame_idx: int, rois: list, ratio: float):
        self.q.append({"frame_id": frame_idx, "rois": rois, "ratio": float(ratio)})

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
