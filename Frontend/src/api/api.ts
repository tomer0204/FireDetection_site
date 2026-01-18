import axios from "axios"

const api = axios.create({
  baseURL: "http://localhost:5000/api",
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
