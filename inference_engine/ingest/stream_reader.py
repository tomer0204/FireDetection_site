import os
import cv2

class StreamReader:
    def __init__(self, source_cfg: dict):
        if source_cfg.get("type") != "video":
            raise NotImplementedError("Only video source supported")

        path = source_cfg["path"]
        if not os.path.exists(path):
            raise RuntimeError(f"Video path does not exist: {path}")

        self.cap = cv2.VideoCapture(path)
        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open video: {path}")

        self.frame_index = 0

    def read(self):
        ok, frame = self.cap.read()
        if not ok:
            return None
        idx = self.frame_index
        self.frame_index += 1
        return idx, frame

    def close(self):
        if self.cap:
            self.cap.release()
