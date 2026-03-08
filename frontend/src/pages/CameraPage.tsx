import { useParams } from "react-router-dom"
import { useEffect, useMemo, useRef, useState } from "react"
import { io, Socket } from "socket.io-client"
import { createStream, getCameraStreams, stopStream } from "../api/cameraStreamApi"
import { CameraStream } from "../types/cameraStream"
import { RealtimeDetection } from "../types/realtimeDetection"
import "../styles/camera.css"

type DetectionsPayload = {
  run_id: string
  frame_index: number
  detections: RealtimeDetection[]
}

export default function CameraPage() {
  const { id } = useParams()
  const cameraId = Number(id)

  const [activeStream, setActiveStream] = useState<CameraStream | null>(null)
  const [loading, setLoading] = useState(false)

  const socketRef = useRef<Socket | null>(null)
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const imageRef = useRef<HTMLImageElement | null>(null)
  const lastUrlRef = useRef<string | null>(null)

  const detectionsRef = useRef<RealtimeDetection[]>([])

  const backendBase = useMemo(() => import.meta.env.VITE_API_BASE_URL, [])

  const cleanup = () => {
    if (lastUrlRef.current) {
      URL.revokeObjectURL(lastUrlRef.current)
      lastUrlRef.current = null
    }
    detectionsRef.current = []
    const canvas = canvasRef.current
    if (canvas) {
      const ctx = canvas.getContext("2d")
      if (ctx) ctx.clearRect(0, 0, canvas.width, canvas.height)
    }
  }

  const disconnectSocket = () => {
    const s = socketRef.current
    socketRef.current = null
    if (s) s.disconnect()
    cleanup()
  }

  const toPixelDets = (img: HTMLImageElement, dets: RealtimeDetection[]) => {
    const w = img.naturalWidth
    const h = img.naturalHeight

    const maxVal = dets.length
      ? Math.max(
          ...dets.flatMap(d => [d.x1, d.y1, d.x2, d.y2].map(v => Math.abs(Number(v) || 0)))
        )
      : 0

    const looksNormalized = maxVal > 0 && maxVal <= 1.5

    return dets
      .map(d => {
        let x1 = Number(d.x1) || 0
        let y1 = Number(d.y1) || 0
        let x2 = Number(d.x2) || 0
        let y2 = Number(d.y2) || 0

        if (looksNormalized) {
          x1 *= w
          x2 *= w
          y1 *= h
          y2 *= h
        }

        const looksXYWH = x2 > 0 && y2 > 0 && (x2 < x1 || y2 < y1)
        if (looksXYWH) {
          x2 = x1 + x2
          y2 = y1 + y2
        }

        if (x2 < x1) [x1, x2] = [x2, x1]
        if (y2 < y1) [y1, y2] = [y2, y1]

        x1 = Math.max(0, Math.min(w, x1))
        y1 = Math.max(0, Math.min(h, y1))
        x2 = Math.max(0, Math.min(w, x2))
        y2 = Math.max(0, Math.min(h, y2))

        return { ...d, x1, y1, x2, y2 }
      })
      .filter(d => d.x2 - d.x1 >= 2 && d.y2 - d.y1 >= 2)
  }

  const draw = (img: HTMLImageElement, dets: RealtimeDetection[]) => {
    const canvas = canvasRef.current
    if (!canvas) return

    const w = img.naturalWidth
    const h = img.naturalHeight
    if (!w || !h) return

    canvas.width = w
    canvas.height = h

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    ctx.clearRect(0, 0, w, h)
    ctx.drawImage(img, 0, 0, w, h)

    const pxDets = toPixelDets(img, dets)

    ctx.lineWidth = Math.max(2, Math.floor(Math.min(w, h) * 0.003))
    ctx.strokeStyle = "#ff0000"
    ctx.font = `${Math.max(14, Math.floor(Math.min(w, h) * 0.02))}px Arial`

    for (const d of pxDets) {
      const x = d.x1
      const y = d.y1
      const ww = d.x2 - d.x1
      const hh = d.y2 - d.y1

      ctx.strokeRect(x, y, ww, hh)

      const label = d.label ?? "fire"
      const score = d.score != null ? ` ${d.score.toFixed(2)}` : ""
      const text = `${label}${score}`

      const tw = ctx.measureText(text).width
      const th = Math.max(16, Math.floor(Math.min(w, h) * 0.03))

      ctx.fillStyle = "rgba(255,0,0,0.85)"
      ctx.fillRect(x, Math.max(0, y - th), tw + 10, th)

      ctx.fillStyle = "#fff"
      ctx.fillText(text, x + 5, Math.max(12, y - 6))
    }
  }

  const handleFrame = (data: any) => {
    const blob = data instanceof Blob ? data : new Blob([data], { type: "image/jpeg" })
    const url = URL.createObjectURL(blob)

    if (lastUrlRef.current) URL.revokeObjectURL(lastUrlRef.current)
    lastUrlRef.current = url

    let img = imageRef.current
    if (!img) {
      img = new Image()
      imageRef.current = img
    }

    img.onload = () => {
      draw(img!, detectionsRef.current)
    }

    img.src = url
  }

  const handleDetections = (payload: DetectionsPayload) => {
    if (!payload || !Array.isArray(payload.detections)) return
    detectionsRef.current = payload.detections

    const img = imageRef.current
    if (img && img.naturalWidth) {
      draw(img, detectionsRef.current)
    }
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

    s.on("frame", handleFrame)
    s.on("detections", handleDetections)

    s.on("stream_error", () => {
      disconnectSocket()
      setActiveStream(null)
    })
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
      const stream = await createStream({ camera_id: cameraId, fps: 17 })
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
        <canvas ref={canvasRef} style={{ width: "100%", height: "100%", display: "block" }} />
        {!activeStream && <div className="camera-placeholder">No live stream</div>}
      </div>

      <div className="camera-controls">
        {!activeStream ? (
          <button className="camera-btn start" onClick={onStart} disabled={loading}>
            ▶ Start Stream
          </button>
        ) : (
          <button className="camera-btn stop" onClick={onStop} disabled={loading}>
            ⏹ Stop Stream
          </button>
        )}
      </div>
    </div>
  )
}