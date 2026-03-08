import http from "./api"
import { Camera } from "../types/camera"

export const getCameras = async (): Promise<Camera[]> => {
  const res = await http.get("/cameras")
  return res.data
}

export const createCamera = async (payload: {
  name: string
  lat: number
  lng: number
}): Promise<Camera> => {
  const res = await http.post("/cameras", payload)
  return res.data
}
