import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { register as registerApi, login as loginApi } from "../api/api"
import { useAuth } from "../context/AuthContext"
import { ShieldCheck, ArrowRight, Loader2, UserPlus } from "lucide-react"

const STATES = [
  "Andhra Pradesh","Assam","Bihar","Chhattisgarh","Delhi","Goa","Gujarat",
  "Haryana","Himachal Pradesh","Jharkhand","Karnataka","Kerala",
  "Madhya Pradesh","Maharashtra","Odisha","Punjab","Rajasthan",
  "Tamil Nadu","Telangana","Uttar Pradesh","Uttarakhand","West Bengal",
]

const LANG_MAP = {
  Hindi:"hi", English:"en", Tamil:"ta", Telugu:"te",
  Bengali:"bn", Marathi:"mr", Gujarati:"gu", Punjabi:"pa",
}

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

// ── Moved OUTSIDE Register to prevent remount on every keystroke ──────────────

function InputField({ label, name, type = "text", placeholder = "", value, onChange }) {
  return (
    <div className="space-y-1.5">
      <label className="block text-sm font-bold text-green-900 ml-1">{label}</label>
      <input
        name={name}
        type={type}
        required
        value={value}
        onChange={onChange}
        className="w-full px-4 py-3 bg-white border-2 border-green-100 rounded-2xl text-green-950 placeholder-green-800/40 focus:outline-none focus:border-green-500 focus:ring-4 focus:ring-green-500/20 transition-all font-medium shadow-sm"
        placeholder={placeholder}
      />
    </div>
  )
}

function SelectField({ label, name, options, value, onChange }) {
  return (
    <div className="space-y-1.5">
      <label className="block text-sm font-bold text-green-900 ml-1">{label}</label>
      <select
        name={name}
        value={value}
        onChange={onChange}
        className="w-full px-4 py-3 bg-white border-2 border-green-100 rounded-2xl text-green-950 focus:outline-none focus:border-green-500 focus:ring-4 focus:ring-green-500/20 transition-all font-medium shadow-sm"
      >
        {options.map(o => <option key={o}>{o}</option>)}
      </select>
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────────────

export default function Register() {
  const { login } = useAuth()
  const navigate  = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState(null)
  const [form, setForm] = useState({
    name:"", age:"", location:"Uttar Pradesh", area:"",
    caste:"General", annual_income:"", gender:"Male",
    pwd_status:"No", language_pref:"Hindi", email:"", password:"",
  })

  const set = (e) => setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (form.password.length < 8) { setError("Password must be at least 8 characters"); return }
    setLoading(true); setError(null)
    try {
      await registerApi({
        name: form.name, age: parseInt(form.age),
        location: form.location, area: form.area,
        caste: form.caste, annual_income: parseFloat(form.annual_income),
        gender: form.gender, pwd_status: form.pwd_status === "Yes",
        language_pref: LANG_MAP[form.language_pref],
        email: form.email, password: form.password,
      })
      const lr = await loginApi({ email: form.email, password: form.password })
      login(lr.data.access_token, { id: lr.data.user_id, name: lr.data.name })
      navigate("/dashboard")
    } catch (err) {
      setError(getApiErrorMessage(err, "Registration failed."))
    } finally { setLoading(false) }
  }

  return (
    <div className="min-h-screen bg-[#f0fdf4] font-sans relative overflow-hidden flex flex-col pt-20 pb-16">

      {/* Background Ornaments */}
      <div className="absolute top-[-10%] right-[-10%] w-[50%] h-[50%] bg-emerald-200/40 rounded-full blur-[120px] pointer-events-none z-0"></div>
      <div className="absolute bottom-[-10%] left-[-10%] w-[50%] h-[50%] bg-green-300/30 rounded-full blur-[120px] pointer-events-none z-0"></div>

      <div className="flex-1 flex items-center justify-center px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="w-full max-w-2xl">

          <div className="bg-white/80 backdrop-blur-xl rounded-[2.5rem] shadow-[0_20px_60px_-15px_rgba(22,163,74,0.2)] border border-white p-6 md:p-10">

            <div className="text-center mb-8">
              <Link to="/" className="inline-flex items-center justify-center h-16 w-16 rounded-full bg-gradient-to-br from-green-500 to-green-700 shadow-lg mb-6 transform hover:scale-105 transition-transform">
                <UserPlus className="h-8 w-8 text-white" />
              </Link>
              <h2 className="text-3xl font-black text-green-950 tracking-tight">Create Profile</h2>
              <p className="text-green-800/70 font-medium mt-2">Set up your account to start finding eligible schemes</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                <InputField label="Full Name"         name="name"          value={form.name}          onChange={set} placeholder="e.g. Ramesh Kumar" />
                <InputField label="Email Address"     name="email"         value={form.email}         onChange={set} type="email"   placeholder="you@example.com" />
                <InputField label="Password"          name="password"      value={form.password}      onChange={set} type="password" placeholder="Min 8 characters" />
                <InputField label="Age"               name="age"           value={form.age}           onChange={set} type="number"  placeholder="e.g. 25" />
                <SelectField label="State"            name="location"      value={form.location}      onChange={set} options={STATES} />
                <InputField label="District / Area"   name="area"          value={form.area}          onChange={set} placeholder="e.g. Lucknow" />
                <SelectField label="Gender"           name="gender"        value={form.gender}        onChange={set} options={["Male", "Female", "Other"]} />
                <SelectField label="Caste Category"   name="caste"         value={form.caste}         onChange={set} options={["General", "OBC", "SC", "ST"]} />
                <InputField label="Annual Income (₹)" name="annual_income" value={form.annual_income} onChange={set} type="number"  placeholder="120000" />
                <SelectField label="Person with Disability?" name="pwd_status"    value={form.pwd_status}    onChange={set} options={["No", "Yes"]} />
                <SelectField label="Preferred Language"      name="language_pref" value={form.language_pref} onChange={set} options={Object.keys(LANG_MAP)} />
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
                className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-green-600 to-green-500 hover:from-green-700 hover:to-green-600 text-white px-8 py-4 rounded-2xl font-bold text-lg transition-all duration-300 shadow-[0_8px_20px_rgba(22,163,74,0.3)] hover:shadow-[0_12px_25px_rgba(22,163,74,0.4)] hover:-translate-y-0.5 disabled:opacity-70 mt-4"
              >
                {loading ? (
                  <><Loader2 className="h-5 w-5 animate-spin" /> Processing...</>
                ) : (
                  <>Create Account <ArrowRight className="h-5 w-5" /></>
                )}
              </button>
            </form>

            <div className="mt-8 text-center text-green-900 font-medium">
              Already have an account?{" "}
              <Link to="/login" className="text-green-600 font-bold hover:text-green-700 hover:underline underline-offset-4 transition-all">
                Login here
              </Link>
            </div>
          </div>

        </div>
      </div>
    </div>
  )
}
