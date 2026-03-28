// src/App.jsx
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import { AuthProvider } from "./context/AuthContext"
import ProtectedRoute from "./components/layout/ProtectedRoute"
import Navbar from "./components/layout/Navbar"

import Landing       from "./pages/Landing"
import Login         from "./pages/Login"
import Register      from "./pages/Register"
import Dashboard     from "./pages/Dashboard"
import SearchResults from "./pages/SearchResults"   // ← styled search page
import SchemeDetail  from "./pages/SchemeDetail"
import Profile       from "./pages/Profile"
import FormPage      from "./pages/FormPage"

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

              {/* /search now uses the fully styled SearchResults page */}
              <Route path="/search" element={
                <ProtectedRoute><SearchResults /></ProtectedRoute>
              }/>

              <Route path="/scheme/:id" element={
                <ProtectedRoute><SchemeDetail /></ProtectedRoute>
              }/>
              <Route path="/profile" element={
                <ProtectedRoute><Profile /></ProtectedRoute>
              }/>
              <Route path="/scheme/:schemeId/form" element={
                <ProtectedRoute><FormPage /></ProtectedRoute>
              }/>

              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </AuthProvider>
  )
}
