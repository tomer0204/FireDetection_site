import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { getCameraStream } from "../api/cameraApi";
import { getTracksByCamera } from "../api/trackApi";
import { getDetectionsByCamera } from "../api/detectionApi";
import { Track } from "../types/track";
import { Detection } from "../types/detection";
import TrackList from "../components/Camera/TrackList";
import DetectionList from "../components/Camera/DetectionList";

export default function CameraPage() {
  const { id } = useParams();
  const cameraId = Number(id);

  const [videoUrl, setVideoUrl] = useState("");
  const [tracks, setTracks] = useState<Track[]>([]);
  const [detections, setDetections] = useState<Detection[]>([]);

  useEffect(() => {
    if (!cameraId) return;

    getCameraStream(cameraId).then(res => setVideoUrl(res.stream_url));
    getTracksByCamera(cameraId).then(setTracks);
    getDetectionsByCamera(cameraId).then(setDetections);
  }, [cameraId]);

  return (
    <div style={{ padding: 16 }}>
      <h2>Camera {cameraId}</h2>

      <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: 16 }}>
        <div>
          <video src={videoUrl} controls autoPlay width="100%" />
        </div>

        <div style={{ overflow: "auto", maxHeight: "80vh" }}>
          <TrackList tracks={tracks} />
          <DetectionList detections={detections} />
        </div>
      </div>
    </div>
  );
}
