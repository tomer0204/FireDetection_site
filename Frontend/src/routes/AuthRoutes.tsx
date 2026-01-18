import { Navigate, Route, Routes } from "react-router-dom"
import LoginPage from "../pages/LoginPage"
import { User } from "../types/user"

type Props = {
  user: User | null
  onLoginSuccess: () => void
}

export default function AuthRoutes({ user, onLoginSuccess }: Props) {
  if (user) {
    return <Navigate to="/" replace />
  }

  return (
    <Routes>
      <Route
        path="/login"
        element={<LoginPage onLoginSuccess={onLoginSuccess} />}
      />
    </Routes>
  )
}
