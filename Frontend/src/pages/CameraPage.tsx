import { useParams } from "react-router-dom"
import { useEffect, useMemo, useRef, useState } from "react"
import { io, Socket } from "socket.io-client"
import { createStream, getCameraStreams, stopStream } from "../api/cameraStreamApi"
import { CameraStream } from "../types/cameraStream"
import "../styles/camera.css"

export default function CameraPage() {
  const { id } = useParams()
  const cameraId = Number(id)

  const [activeStream, setActiveStream] = useState<CameraStream | null>(null)
  const [loading, setLoading] = useState(false)
  const [frameUrl, setFrameUrl] = useState<string | null>(null)

  const socketRef = useRef<Socket | null>(null)
  const lastUrlRef = useRef<string | null>(null)

  const backendBase = useMemo(
    () => import.meta.env.VITE_API_BASE_URL,
    []
  )

  const cleanupFrameUrl = () => {
    if (lastUrlRef.current) {
      URL.revokeObjectURL(lastUrlRef.current)
      lastUrlRef.current = null
    }
    setFrameUrl(null)
  }

  const disconnectSocket = () => {
    const s = socketRef.current
    socketRef.current = null
    if (s) s.disconnect()
    cleanupFrameUrl()
  }

  const connectAndJoin = (streamId: number) => {
    disconnectSocket()

    const s = io(backendBase, {
      withCredentials: true,
      transports: ["websocket"]
    })

    socketRef.current = s

    s.on("connect", () => {
      s.emit("join_stream", { stream_id: streamId })
    })

    s.on("frame", (data: ArrayBuffer) => {
      const blob = new Blob([data], { type: "image/jpeg" })
      const url = URL.createObjectURL(blob)
      if (lastUrlRef.current) URL.revokeObjectURL(lastUrlRef.current)
      lastUrlRef.current = url
      setFrameUrl(url)
    })

    s.on("stream_error", () => {
      disconnectSocket()
      setActiveStream(null)
    })

    s.on("disconnect", cleanupFrameUrl)
  }

  useEffect(() => {
    if (!cameraId) return

    getCameraStreams(cameraId).then(streams => {
      const active = streams.find(s => s.is_active)
      if (active) {
        setActiveStream(active)
        connectAndJoin(active.stream_id)
      }
    })

    return () => disconnectSocket()
  }, [cameraId])

  const onStart = async () => {
    if (loading || activeStream) return
    setLoading(true)
    try {
      const stream = await createStream({ camera_id: cameraId, fps: 10 })
      setActiveStream(stream)
      connectAndJoin(stream.stream_id)
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
      disconnectSocket()
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="camera-page">
      <div className="camera-video">
        {frameUrl ? (
          <img src={frameUrl} />
        ) : (
          <div className="camera-placeholder">
            No live stream
          </div>
        )}
      </div>

      <div className="camera-controls">
        {!activeStream ? (
          <button
            className="camera-btn start"
            onClick={onStart}
            disabled={loading}
          >
            ▶ Start Stream
          </button>
        ) : (
          <button
            className="camera-btn stop"
            onClick={onStop}
            disabled={loading}
          >
            ⏹ Stop Stream
          </button>
        )}
      </div>
    </div>
  )
}
