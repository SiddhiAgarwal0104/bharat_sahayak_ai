// src/api/api.js
import axios from "axios"

const BASE_URL = import.meta.env.VITE_BACKEND_URL || "http://127.0.0.1:8000"

// Axios instance — automatically adds JWT to every request
const api = axios.create({ baseURL: BASE_URL })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token")
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// ── Auth ───────────────────────────────────────────────────────────────────────
export const register = (data) => api.post("/auth/register", data)
export const login    = (data) => api.post("/auth/login", data)
export const getMe    = ()     => api.get("/auth/me")
export const updateMe = (data) => api.put("/auth/me", data)

// ── Schemes ────────────────────────────────────────────────────────────────────
export const getRecommended = ()   => api.get("/schemes/recommended")
export const getScheme      = (id) => api.get(`/schemes/${id}`)

// ── Query (text or audio) ──────────────────────────────────────────────────────
export const queryText = (text, language) => {
  console.log(`[API] queryText: "${text.substring(0, 50)}..."`)
  return api.post("/form/query", { input_type: "text", content: text })
}

export const queryAudio = (audioBlob, languageHint) => {
  console.log(`[API] queryAudio: blob size=${audioBlob.size}, language_hint=${languageHint}`)
  const form = new FormData()
  form.append("audio", audioBlob, "recording.webm")
  if (languageHint) form.append("language_hint", languageHint)
  return api.post("/stt/transcribe", form, {
    headers: { "Content-Type": "multipart/form-data" },
  })
}

export const sendChatMessage = (message) => {
  return api.post("/chatbot/chat", { message })
}

export default api