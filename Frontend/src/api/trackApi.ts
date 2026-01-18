import http from "./api";
import { Track } from "../types/track";

export const getTracksByCamera = async (cameraId: number): Promise<Track[]> => {
  const res = await http.get(`/cameras/${cameraId}/tracks`);
  return res.data;
};
