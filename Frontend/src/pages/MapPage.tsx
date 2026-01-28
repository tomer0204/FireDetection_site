import { useEffect, useState } from "react"
import IsraelMap from "../components/Map/IsraelMap"
import { Camera } from "../types/camera"
import { getCameras } from "../api/cameraApi"
import "../styles/layout.css"

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
