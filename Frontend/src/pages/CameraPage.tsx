import { useEffect, useState } from "react"
import { useParams } from "react-router-dom"
import { getCameraStream, startCameraStream, stopCameraStream } from "../api/cameraStreamApi"
import { CameraStream } from "../types/cameraStream"

export default function CameraPage() {
  const { id } = useParams()
  const cameraId = Number(id)

  const [stream, setStream] = useState<CameraStream | null>(null)
  const [frameUrl, setFrameUrl] = useState("")

  useEffect(() => {
    getCameraStream(cameraId).then(res => {
      if (res.is_active && res.stream) setStream(res.stream)
      else setStream(null)
    })
  }, [cameraId])

  const startLive = async () => {
    const res = await startCameraStream(cameraId, {
      source_ref: "fire_real.mp4",
      fps: 17
    })
    setStream(res.stream)
  }

  const stopLive = async () => {
    await stopCameraStream(cameraId)
    setStream(null)
  }

  useEffect(() => {
    if (!stream || !stream.is_active) return

    const interval = setInterval(() => {
      setFrameUrl(`/api/cameras/${cameraId}/frame?ts=${Date.now()}`)
    }, 200)

    return () => clearInterval(interval)
  }, [stream, cameraId])

  return (
    <div style={{ padding: 16 }}>
      <h2>Camera {cameraId}</h2>

      {!stream && <button onClick={startLive}>Start Live</button>}
      {stream && <button onClick={stopLive}>Stop Live</button>}

      <div style={{ marginTop: 16 }}>
        {stream ? <img src={frameUrl} width="100%" /> : <div>No active stream</div>}
      </div>
    </div>
  )
}
