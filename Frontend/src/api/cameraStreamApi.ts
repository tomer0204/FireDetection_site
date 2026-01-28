import http from "./api"
import { CameraStream } from "../types/cameraStream"

export const getCameraStream = async (
  cameraId: number
): Promise<{ is_active: boolean; stream?: CameraStream }> => {
  const res = await http.get(`/cameras/${cameraId}/stream`)
  return res.data
}

export const startCameraStream = async (
  cameraId: number,
  payload: { source_ref: string; fps?: number }
): Promise<{ stream: CameraStream }> => {
  const res = await http.post(`/cameras/${cameraId}/start`, payload)
  return res.data
}

export const stopCameraStream = async (cameraId: number) => {
  const res = await http.post(`/cameras/${cameraId}/stop`)
  return res.data
}
