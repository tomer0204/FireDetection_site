import http from "./api"
import { CameraStream } from "../types/cameraStream"

export const getCameraStreams = async (cameraId: number): Promise<CameraStream[]> => {
  const res = await http.get(`/cameras/${cameraId}/streams`)
  return res.data
}

export const createStream = async (payload: { camera_id: number; fps: number }): Promise<CameraStream> => {
  const res = await http.post("/streams", payload)
  return res.data
}

export const stopStream = async (streamId: number) => {
  const res = await http.post(`/streams/${streamId}/stop`)
  return res.data
}
