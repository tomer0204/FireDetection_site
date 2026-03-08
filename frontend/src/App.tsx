import { useEffect, useState } from "react"
import AppRoutes from "./routes/AppRoutes"
import { me } from "./api/authApi"

export default function App() {
  const [authed, setAuthed] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    me()
      .then(() => setAuthed(true))
      .catch(() => setAuthed(false))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return null

  return <AppRoutes authed={authed} setAuthed={setAuthed} />
}
