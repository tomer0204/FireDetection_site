import { Outlet, useNavigate } from "react-router-dom"
import { logout } from "../../api/authApi"
import "../../styles/layout.css"

type Props = {
  onLogout: () => void
}

export default function MainLayout({ onLogout }: Props) {
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    onLogout()
    navigate("/login")
  }

  return (
    <div className="layout-root">
      <header className="layout-header">
        <div className="layout-title">Fire Detection</div>
        <button className="layout-logout" onClick={handleLogout} title="Logout from system">
        Logout
        </button>
      </header>

      <main className="layout-main">
        <Outlet />
      </main>
    </div>
  )
}
