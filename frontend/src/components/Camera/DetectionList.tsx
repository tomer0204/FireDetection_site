import { Detection } from "../../types/detection";

export default function DetectionList({ detections }: { detections: Detection[] }) {
  return (
    <div>
      <h3>Detections</h3>
      {detections.length === 0 ? (
        <div>No detections</div>
      ) : (
        <ul>
          {detections.map(d => (
            <li key={d.detection_id}>
              det_id={d.detection_id} | track_id={d.track_id} | box=({d.coordinates.x1},{d.coordinates.y1})-({d.coordinates.x2},{d.coordinates.y2}) | {d.created_at}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
