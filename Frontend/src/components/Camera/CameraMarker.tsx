import { Marker, Popup } from "react-leaflet";
import { useNavigate } from "react-router-dom";
import { Camera } from "../../types/camera";

export default function CameraMarker({ camera }: { camera: Camera }) {
  const navigate = useNavigate();

  return (
    <Marker position={[camera.latitude, camera.longitude]}>
      <Popup>
        <div>Camera #{camera.camera_id}</div>
        <button onClick={() => navigate(`/camera/${camera.camera_id}`)}>
          Open Camera
        </button>
      </Popup>
    </Marker>
  );
}
