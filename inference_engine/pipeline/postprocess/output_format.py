def refine_bbox(bbox, frame_shape, margin=5):
    h, w = frame_shape[:2]
    x1, y1, x2, y2 = bbox

    x1 = max(0, x1 - margin)
    y1 = max(0, y1 - margin)
    x2 = min(w - 1, x2 + margin)
    y2 = min(h - 1, y2 + margin)

    return (x1, y1, x2, y2)
