export interface DetectionCoordinates {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface Detection {
  detection_id: number;
  camera_id: number;
  track_id: number;
  coordinates: DetectionCoordinates;
  created_at: string;
  updated_at: string;
}
