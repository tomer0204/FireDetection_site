export type UserRole = "viewer" | "admin"

export type User = {
  id: number
  email: string
  username: string
  role: UserRole
  created_at: string
  updated_at: string
}
