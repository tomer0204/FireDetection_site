from app.model.detection import Detection

def get_detections_by_camera(camera_id):
    return Detection.query.filter_by(camera_id=camera_id).all()
