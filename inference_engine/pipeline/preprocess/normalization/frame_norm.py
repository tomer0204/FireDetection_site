import cv2
import numpy as np

def normalize_rgb(frame):
    return frame.astype(np.float32) / 255.0

def normalize_ycrcb(frame):
    ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
    return ycrcb.astype(np.float32)
