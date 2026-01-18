import api from "./api"
import { User } from "../types/user"

export async function register(email: string, username: string, password: string): Promise<User> {
  const res = await api.post("/auth/register", { email, username, password })
  return res.data.user
}

export async function login(username: string, password: string): Promise<User> {
  const res = await api.post("/auth/login", { username, password })
  return res.data.user
}

export async function logout() {
  await api.post("/auth/logout")
}

export async function me(): Promise<User> {
  const res = await api.get("/auth/me")
  return res.data.user
}
