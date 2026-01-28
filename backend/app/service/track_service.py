from app.model.track import Track

def get_tracks_by_camera(camera_id):
    return Track.query.filter_by(camera_id=camera_id).all()
