import yaml

def load_cameras(config_path: str):
    with open(config_path, "r") as f:
        data = yaml.safe_load(f) or {}
    cams = data.get("cameras", [])
    return {str(c["camera_id"]): c for c in cams}
