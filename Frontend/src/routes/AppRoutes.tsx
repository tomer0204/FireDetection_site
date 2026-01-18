import { Routes, Route, Navigate } from "react-router-dom"
import MainLayout from "../components/Layout/MainLayout"
import MapPage from "../pages/MapPage"
import CameraPage from "../pages/CameraPage"
import LoginPage from "../pages/LoginPage"

type Props = {
  authed: boolean
  setAuthed: (v: boolean) => void
}

export default function AppRoutes({ authed, setAuthed }: Props) {
  return (
    <Routes>
      <Route
        path="/login"
        element={
          authed ? (
            <Navigate to="/" replace />
          ) : (
            <LoginPage onLoginSuccess={() => setAuthed(true)} />
          )
        }
      />

      <Route
        element={
          authed ? (
            <MainLayout onLogout={() => setAuthed(false)} />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      >
        <Route path="/" element={<MapPage />} />
        <Route path="/camera/:id" element={<CameraPage />} />
      </Route>

      <Route path="*" element={<Navigate to={authed ? "/" : "/login"} replace />} />
    </Routes>
  )
}
