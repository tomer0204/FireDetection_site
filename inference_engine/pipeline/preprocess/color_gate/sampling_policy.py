def should_check_color(frame_idx: int, every_n: int) -> bool:
    if every_n <= 1:
        return True
    return frame_idx % every_n == 0

def should_run_yolo(frame_idx: int, suspicious: bool, cooldown_state: dict, cooldown_frames: int) -> bool:
    left = int(cooldown_state.get("cooldown_left", 0))
    if left > 0:
        cooldown_state["cooldown_left"] = left - 1
        return False
    if suspicious:
        cooldown_state["cooldown_left"] = int(cooldown_frames)
        return True
    return False
