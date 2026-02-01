import axios from "axios"

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL + "/api",
  withCredentials: true
})

api.interceptors.request.use(config => {
  const csrf = document.cookie
    .split("; ")
    .find(x => x.startsWith("csrf_access_token="))
    ?.split("=")[1]

  if (csrf) {
    config.headers["X-CSRF-TOKEN"] = csrf
  }

  return config
})

export default api
