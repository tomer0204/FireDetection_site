import {useEffect, useState} from "react";
import {getCameras} from "../api/cameraApi";
import {Camera} from "../types/camera";
import IsraelMap from "../components/Map/IsraelMap";

export default function MapPage() {
  const [cameras, setCameras] = useState<Camera[]>([])

  useEffect(() => {
    getCameras().then(setCameras).catch(() => setCameras([]))
  }, [])

  return (
    <div className="map-page">
      <IsraelMap cameras={cameras} />
    </div>
  )
}
