import { Navigate, Route, Routes } from "react-router-dom"
import MainLayout from "../components/Layout/MainLayout"
import MapPage from "../pages/MapPage"
import CameraPage from "../pages/CameraPage"
import { User } from "../types/user"

type Props = {
  user: User | null
  onLogout: () => void
}

export default function ProtectedRoutes({ user, onLogout }: Props) {
  if (!user) {
    return <Navigate to="/login" replace />
  }

  return (
    <Routes>
      <Route element={<MainLayout user={user} onLogoutSuccess={onLogout}  />}>
        <Route path="/" element={<MapPage />} />
        <Route path="/camera/:id" element={<CameraPage />} />
      </Route>
    </Routes>
  )
}
