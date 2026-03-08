from pipeline.preprocess.color_gate import color_gate
def process_frame(frame, ctx):
    if ctx.current_state == "COLOR_GATE":
        rois = color_gate(frame)
        if not rois:
            return None
        ctx.active_rois = rois
        ctx.current_state = "CNN_GATE"

    if ctx.current_state == "CNN_GATE":
        detections = cnn_detect(frame, ctx.active_rois)
        if not detections:
            ctx.current_state = "COLOR_GATE"
            return None
        ctx.active_rois = detections
        ctx.current_state = "TEMPORAL_ACCUMULATION"

    if ctx.current_state == "TEMPORAL_ACCUMULATION":
        stable = update_temporal_features(frame, ctx)
        if not stable:
            return None
        ctx.current_state = "PIXEL_SEGMENTATION"

    if ctx.current_state == "PIXEL_SEGMENTATION":
        mask = mrf_segment(frame, ctx.active_rois)
        if mask.pixel_ratio < THRESH:
            ctx.current_state = "CNN_GATE"
            return None
        ctx.current_state = "TEMPORAL_SMOOTHING"

    if ctx.current_state == "TEMPORAL_SMOOTHING":
        if not temporal_smooth(ctx):
            ctx.current_state = "CNN_GATE"
            return None
        return final_decision(ctx)
