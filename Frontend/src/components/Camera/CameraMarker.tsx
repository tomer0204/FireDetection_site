import { Marker, Popup } from "react-leaflet"
import { useNavigate } from "react-router-dom"
import { Camera } from "../../types/camera"
import L from "leaflet"
import cameraIconImg from "../../assets/camera.png"

const cameraIcon = new L.Icon({
  iconUrl: cameraIconImg,
  iconSize: [28, 28],
  iconAnchor: [14, 28],
  popupAnchor: [0, -28]
})

export default function CameraMarker({ camera }: { camera: Camera }) {
  const navigate = useNavigate()

  return (
    <Marker
      position={[camera.lat, camera.lng]}
      icon={cameraIcon}
      eventHandlers={{
        click: () => navigate(`/camera/${camera.camera_id}`)
      }}
    >
      <Popup>
        <strong>{camera.name}</strong>
      </Popup>
    </Marker>
  )
}
