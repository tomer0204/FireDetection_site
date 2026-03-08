class OrchestratorContext:
    def __init__(self, camera_id: int, run_id: str, fps: int):
        self.camera_id = int(camera_id)
        self.run_id = str(run_id)
        self.fps = int(fps)

        self.frame_index = 0
        self.cooldown = {"cooldown_left": 0}

        self.last_color_ratio = 0.0
        self.last_color_suspicious = False
        self.last_rois = []
