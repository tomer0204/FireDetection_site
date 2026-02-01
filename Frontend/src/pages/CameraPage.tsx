import { useParams } from "react-router-dom"
import { useEffect, useState } from "react"
import {
  createStream,
  getCameraStreams,
  stopStream
} from "../api/cameraStreamApi"
import { CameraStream } from "../types/cameraStream"
import cameraImg from "../assets/camera.png"

export default function CameraPage() {
  const { id } = useParams()
  const cameraId = Number(id)

  const [activeStream, setActiveStream] = useState<CameraStream | null>(null)
  const [liveUrl, setLiveUrl] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!cameraId) return

    getCameraStreams(cameraId).then(streams => {
      const active = streams.find(s => s.is_active)
      if (active) {
        setActiveStream(active)
        setLiveUrl(`/api/streams/${cameraId}/live`)
      }
    })
  }, [cameraId])

  const onStart = async () => {
  if (loading || activeStream) return

  setLoading(true)
  try {
    const stream = await createStream({
      camera_id: cameraId,
      fps: 10
    })

    setActiveStream(stream)
    setLiveUrl(`/api/streams/${stream.stream_id}/live`)
  } finally {
    setLoading(false)
  }
}


  const onStop = async () => {
    if (!activeStream) return

    setLoading(true)
    try {
      await stopStream(activeStream.stream_id)
      setActiveStream(null)
      setLiveUrl(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ padding: 16 }}>
      <h2>Camera {cameraId}</h2>


      <div style={{ marginBottom: 12 }}>
        <img
          src={cameraImg}
          alt="Camera"
          style={{
            width: 80,
            opacity: activeStream ? 1 : 0.5
          }}
        />
      </div>

      <div style={{ marginBottom: 12 }}>
        {!activeStream ? (
          <button onClick={onStart} disabled={loading}>
            ▶ Start Stream
          </button>
        ) : (
          <button onClick={onStop} disabled={loading}>
            ⏹ Stop Stream
          </button>
        )}
      </div>

      {liveUrl && (
        <img
          src={liveUrl}
          style={{
            width: "100%",
            maxWidth: 900,
            border: "1px solid #333"
          }}
        />
      )}
    </div>
  )
}
