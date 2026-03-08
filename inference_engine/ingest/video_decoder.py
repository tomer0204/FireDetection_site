import cv2

class VideoDecoder:
    def __init__(self, path):
        self.cap = cv2.VideoCapture(path)

    def read(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

    def release(self):
        self.cap.release()
