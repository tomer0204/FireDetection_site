import { Outlet, useNavigate, useLocation } from "react-router-dom"
import { logout } from "../../api/authApi"
import "../../styles/layout.css"

type Props = {
  onLogout: () => void
}

export default function MainLayout({ onLogout }: Props) {
  const navigate = useNavigate()
  const location = useLocation()
  const isCameraPage = location.pathname.startsWith("/camera")

  const handleLogout = async () => {
    await logout()
    onLogout()
    navigate("/login")
  }

  return (
    <div className={`layout-root ${isCameraPage ? "camera-layout" : ""}`}>
      <header className="layout-header">
        <div className="layout-left">
          {isCameraPage && (
            <button
              className="layout-back"
              onClick={() => navigate("/")}
            >
              ← Map
            </button>
          )}
          <div className="layout-title">
            {isCameraPage ? "Live Camera" : "Fire Detection"}
          </div>
        </div>

        <button
          className="layout-logout"
          onClick={handleLogout}
        >
          Logout
        </button>
      </header>

      <main className="layout-main">
        <Outlet />
      </main>
    </div>
  )
}
