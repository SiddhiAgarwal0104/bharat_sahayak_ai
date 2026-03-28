// src/App.jsx
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import { AuthProvider } from "./context/AuthContext"
import ProtectedRoute from "./components/layout/ProtectedRoute"
import Navbar from "./components/layout/Navbar"

import Landing      from "./pages/Landing"
import Login        from "./pages/Login"
import Register     from "./pages/Register"
import Dashboard    from "./pages/Dashboard"
import Search       from "./pages/Search"
import SchemeDetail from "./pages/SchemeDetail"
import Profile      from "./pages/Profile"

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="min-h-screen flex flex-col">
          <Navbar />
          <main className="flex-1">
            <Routes>
              <Route path="/"         element={<Landing />} />
              <Route path="/login"    element={<Login />} />
              <Route path="/register" element={<Register />} />

              <Route path="/dashboard" element={
                <ProtectedRoute><Dashboard /></ProtectedRoute>
              }/>
              <Route path="/search" element={
                <ProtectedRoute><Search /></ProtectedRoute>
              }/>
              <Route path="/scheme/:id" element={
                <ProtectedRoute><SchemeDetail /></ProtectedRoute>
              }/>
              <Route path="/profile" element={
                <ProtectedRoute><Profile /></ProtectedRoute>
              }/>

              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </AuthProvider>
  )
}