import http from "./api";
import { Camera } from "../types/camera";

export const getCameras = async (): Promise<Camera[]> => {
  const res = await http.get("/cameras");
  return res.data;
};

export const getCameraStream = async (cameraId: number): Promise<{ stream_url: string }> => {
  const res = await http.get(`/cameras/${cameraId}/stream`);
  return res.data;
};
