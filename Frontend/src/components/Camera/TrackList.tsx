import { Track } from "../../types/track";

export default function TrackList({ tracks }: { tracks: Track[] }) {
  return (
    <div>
      <h3>Tracks</h3>
      {tracks.length === 0 ? (
        <div>No tracks</div>
      ) : (
        <ul>
          {tracks.map(t => (
            <li key={t.track_id}>
              track_id={t.track_id} | created_at={t.created_at}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
