import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { login as loginApi } from "../api/api"
import { useAuth } from "../context/AuthContext"
import { ShieldCheck, ArrowRight, Loader2 } from "lucide-react"

function getApiErrorMessage(err, fallback) {
  const detail = err?.response?.data?.detail
  if (Array.isArray(detail)) {
    const msgs = detail.map((d) => d?.msg).filter(Boolean)
    if (msgs.length) return msgs.join(", ")
  }
  if (typeof detail === "string" && detail.trim()) return detail
  if (detail && typeof detail === "object" && typeof detail.msg === "string") return detail.msg
  return fallback
}

export default function Login() {
  const { login } = useAuth()
  const navigate  = useNavigate()
  const [form,    setForm]    = useState({ email: "", password: "" })
  const [error,   setError]   = useState(null)
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const res = await loginApi(form)
      login(res.data.access_token, {
        id: res.data.user_id, name: res.data.name,
      })
      navigate("/dashboard")
    } catch (err) {
      setError(getApiErrorMessage(err, "Login failed. Check your credentials."))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#f0fdf4] font-sans relative overflow-hidden flex flex-col pt-20">
      
      {/* Background Ornaments */}
      <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-emerald-200/40 rounded-full blur-[120px] pointer-events-none z-0"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-green-300/30 rounded-full blur-[120px] pointer-events-none z-0"></div>

      <div className="flex-1 flex items-center justify-center px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="w-full max-w-md">
          
          <div className="bg-white/80 backdrop-blur-xl rounded-[2.5rem] shadow-[0_20px_60px_-15px_rgba(22,163,74,0.2)] border border-white p-8 md:p-10">
            
            {/* Header */}
            <div className="text-center mb-10">
              <Link to="/" className="inline-flex items-center justify-center h-16 w-16 rounded-full bg-gradient-to-br from-green-500 to-green-700 shadow-lg mb-6 transform hover:scale-105 transition-transform">
                <ShieldCheck className="h-8 w-8 text-white" />
              </Link>
              <h2 className="text-3xl font-black text-green-950 tracking-tight">Welcome Back</h2>
              <p className="text-green-800/70 font-medium mt-2">Sign in to SahayakAI to access schemes</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              
              <div className="space-y-1.5">
                <label className="block text-sm font-bold text-green-900 ml-1">Email Address</label>
                <input 
                  name="email" type="email" required
                  value={form.email} onChange={handleChange}
                  className="w-full px-5 py-4 bg-white border-2 border-green-100 rounded-2xl text-green-950 placeholder-green-800/40 focus:outline-none focus:border-green-500 focus:ring-4 focus:ring-green-500/20 transition-all font-medium shadow-sm" 
                  placeholder="you@example.com" 
                />
              </div>

              <div className="space-y-1.5">
                <div className="flex items-center justify-between ml-1">
                  <label className="block text-sm font-bold text-green-900">Password</label>
                  <a href="#" className="text-xs font-bold text-green-600 hover:text-green-700">Forgot password?</a>
                </div>
                <input 
                  name="password" type="password" required
                  value={form.password} onChange={handleChange}
                  className="w-full px-5 py-4 bg-white border-2 border-green-100 rounded-2xl text-green-950 placeholder-green-800/40 focus:outline-none focus:border-green-500 focus:ring-4 focus:ring-green-500/20 transition-all font-medium shadow-sm" 
                  placeholder="••••••••" 
                />
              </div>

              {error && (
                <div className="bg-red-50 text-red-600 text-sm font-semibold rounded-2xl p-4 border border-red-100 flex items-center gap-3">
                  <span className="flex-shrink-0 w-1.5 h-1.5 rounded-full bg-red-500"></span>
                  {error}
                </div>
              )}

              <button 
                type="submit" 
                disabled={loading} 
                className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-green-600 to-green-500 hover:from-green-700 hover:to-green-600 text-white px-8 py-4 rounded-2xl font-bold text-lg transition-all duration-300 shadow-[0_8px_20px_rgba(22,163,74,0.3)] hover:shadow-[0_12px_25px_rgba(22,163,74,0.4)] hover:-translate-y-0.5 disabled:opacity-70 disabled:pointer-events-none mt-2"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin" /> Verifyng...
                  </>
                ) : (
                  <>
                    Sign In <ArrowRight className="h-5 w-5" />
                  </>
                )}
              </button>

            </form>

            <div className="mt-8 text-center text-green-900 font-medium">
              Don't have an account?{" "}
              <Link to="/register" className="text-green-600 font-bold hover:text-green-700 hover:underline underline-offset-4 transition-all">
                Create one now
              </Link>
            </div>
            
          </div>
        </div>
      </div>
    </div>
  )
}