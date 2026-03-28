// src/context/AuthContext.jsx
import { createContext, useContext, useState, useEffect } from "react"
import { getMe } from "../api/api"

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user,    setUser]    = useState(null)
  const [token,   setToken]   = useState(localStorage.getItem("token"))
  const [loading, setLoading] = useState(true)

  const refreshUser = async () => {
    const r = await getMe()
    setUser(r.data)
    return r.data
  }

  // On mount — if token exists, fetch user profile
  useEffect(() => {
    if (token) {
      refreshUser()
        .catch(() => { localStorage.removeItem("token"); setToken(null) })
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [token])

  const loginFn = (token, userData) => {
    localStorage.setItem("token", token)
    setToken(token)
    setUser(userData)
  }

  const logout = () => {
    localStorage.removeItem("token")
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, token, loading, login: loginFn, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)