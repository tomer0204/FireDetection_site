import http from "./api";
import { Detection } from "../types/detection";

export const getDetectionsByCamera = async (cameraId: number): Promise<Detection[]> => {
  const res = await http.get(`/cameras/${cameraId}/detections`);
  return res.data;
};
