import { useEffect, useState } from "react"
import IsraelMap from "../components/Map/IsraelMap"
import { Camera } from "../types/camera"
import "../styles/layout.css"

export default function MapPage() {
  const [cameras, setCameras] = useState<Camera[]>([])

  useEffect(() => {
    setCameras([])
  }, [])

  return (
    <div className="map-page">
      <IsraelMap cameras={cameras} />
    </div>
  )
}
