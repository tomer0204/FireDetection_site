export interface CameraStream {
  stream_id: number
  camera_id: number

  run_id: string

  source_type: string
  source_ref: string

  fps: number
  s3_prefix: string

  started_at: string
  ended_at?: string | null

  is_active: boolean
}
