import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { useAuth } from "../context/AuthContext"
import { updateMe } from "../api/api"
import { tr } from "../utils/i18n"
import { User, LogOut, Edit3, Save, X, ShieldCheck, MapPin, Briefcase, IndianRupee } from "lucide-react"

const getFieldLabels = (lang) => ({
  name: tr(lang, "profile.fullName"), email: tr(lang, "profile.email"), age: tr(lang, "profile.age"),
  location: tr(lang, "profile.state"), area: tr(lang, "profile.district"), caste: tr(lang, "profile.caste"),
  annual_income: tr(lang, "profile.income"), gender: tr(lang, "profile.gender"),
  language_pref: tr(lang, "profile.language"), pwd_status: tr(lang, "profile.pwd"),
})

const LANG_NAMES = {
  hi:"Hindi", en:"English", ta:"Tamil", te:"Telugu",
  bn:"Bengali", mr:"Marathi", gu:"Gujarati", pa:"Punjabi",
}

const GENDER_NAMES = { M:"Male", F:"Female", O:"Other", Male:"Male", Female:"Female", Other:"Other" }

export default function Profile() {
  const { user, logout, refreshUser } = useAuth()
  const lang = user?.language_pref || "en"
  const FIELD_LABELS = getFieldLabels(lang)
  const navigate = useNavigate()
  
  const [isEditing, setIsEditing] = useState(false)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState("")
  const [error, setError] = useState("")
  
  const [form, setForm] = useState({
    name: "", age: "", location: "", area: "", caste: "",
    annual_income: "", gender: "Male", language_pref: "hi", pwd_status: false,
  })

  useEffect(() => {
    if (!user) return
    setForm({
      name: user.name ?? "",
      age: user.age ?? "",
      location: user.location ?? "",
      area: user.area ?? "",
      caste: user.caste ?? "",
      annual_income: user.annual_income ?? "",
      gender: user.gender === "M" ? "Male" : user.gender === "F" ? "Female" : user.gender === "O" ? "Other" : (user.gender ?? "Male"),
      language_pref: user.language_pref ?? "hi",
      pwd_status: Boolean(user.pwd_status),
    })
  }, [user])

  const displayValue = (key, value) => {
    if (key === "language_pref") return LANG_NAMES[value] || value
    if (key === "gender")        return GENDER_NAMES[value] || value
    if (key === "pwd_status")    return value ? tr(lang, "profile.yes") : tr(lang, "profile.no")
    if (key === "annual_income") return `₹${Number(value || 0).toLocaleString()}`
    return value ?? "—"
  }

  const setField = (e) => {
    const { name, value, type, checked } = e.target
    setForm((prev) => ({ ...prev, [name]: type === "checkbox" ? checked : value }))
  }

  const handleSave = async (e) => {
    e.preventDefault()
    setSaving(true)
    setError(""); setMessage("")
    try {
      await updateMe({
        name: form.name, age: Number(form.age), location: form.location, area: form.area,
        caste: form.caste, annual_income: Number(form.annual_income), gender: form.gender,
        language_pref: form.language_pref, pwd_status: Boolean(form.pwd_status),
      })
      await refreshUser()
      setIsEditing(false)
      setMessage(tr(lang, "profile.updated"))
    } catch (err) {
      const detail = err?.response?.data?.detail
      setError(typeof detail === "string" ? detail : tr(lang, "profile.updateFailed"))
    } finally {
      setSaving(false)
    }
  }

  const InputField = ({ label, name, type="text" }) => (
    <div className="space-y-1">
      <label className="block text-sm font-bold text-green-900 ml-1">{label}</label>
      <input 
        name={name} type={type} required value={form[name]} onChange={setField} 
        className="w-full px-4 py-3 bg-white border-2 border-green-100 rounded-2xl text-green-950 focus:outline-none focus:border-green-500 focus:ring-4 focus:ring-green-500/20 transition-all font-medium shadow-sm" 
      />
    </div>
  )

  const SelectField = ({ label, name, options }) => (
    <div className="space-y-1">
      <label className="block text-sm font-bold text-green-900 ml-1">{label}</label>
      <select 
        name={name} value={form[name]} onChange={setField} 
        className="w-full px-4 py-3 bg-white border-2 border-green-100 rounded-2xl text-green-950 focus:outline-none focus:border-green-500 focus:ring-4 focus:ring-green-500/20 transition-all font-medium shadow-sm"
      >
        {options.map(o => <option key={o.value || o.label || o}>{o.label || o}</option>)}
      </select>
    </div>
  )

  if (!user) return null;

  return (
    <div className="bg-[#f0fdf4] min-h-screen pb-20 pt-[100px] relative">
      
      {/* Background elements */}
      <div className="absolute top-0 left-0 w-full h-[300px] bg-gradient-to-b from-green-100/60 to-[#f0fdf4] pointer-events-none z-0"></div>
      <div className="absolute top-20 right-10 w-[300px] h-[300px] bg-emerald-200/40 rounded-full blur-[100px] pointer-events-none z-0"></div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 relative z-10">
        
        {/* Profile Header */}
        <div className="bg-white/80 backdrop-blur-xl rounded-[2.5rem] p-8 md:p-12 mb-8 shadow-[0_20px_60px_-15px_rgba(22,163,74,0.15)] border border-white flex flex-col items-center">
          <div className="relative mb-6 group">
            <div className="absolute inset-0 bg-green-400 rounded-full blur-xl opacity-20 group-hover:opacity-40 transition-opacity"></div>
            <div className="w-28 h-28 bg-gradient-to-br from-green-500 to-emerald-700 rounded-full flex items-center justify-center relative shadow-[0_10px_25px_rgba(22,163,74,0.3)] border-4 border-white">
              <span className="text-white text-5xl font-black">
                {user.name?.[0]?.toUpperCase() || "U"}
              </span>
            </div>
            <div className="absolute bottom-0 right-0 bg-white p-2 rounded-full shadow-lg border border-green-50 text-green-600">
              <ShieldCheck className="h-5 w-5" />
            </div>
          </div>
          <h1 className="text-3xl font-black text-green-950 mb-1 tracking-tight">{user.name}</h1>
          <p className="text-lg text-green-700 font-medium mb-6">{user.email}</p>

          <div className="flex flex-wrap items-center justify-center gap-4">
            <div className="flex items-center gap-2 px-4 py-2 bg-green-50 rounded-xl text-green-800 font-semibold border border-green-100">
              <MapPin className="h-4 w-4 text-green-500" /> {user.location}, {user.area}
            </div>
            <div className="flex items-center gap-2 px-4 py-2 bg-green-50 rounded-xl text-green-800 font-semibold border border-green-100">
              <IndianRupee className="h-4 w-4 text-green-500" /> {user.annual_income?.toLocaleString()}
            </div>
          </div>
        </div>

        {/* Profile Form/Details */}
        <div className="bg-white rounded-[2.5rem] p-8 md:p-10 shadow-[0_10px_40px_rgba(22,163,74,0.05)] border border-green-50 relative overflow-hidden">
          
          <div className="flex items-center justify-between mb-8 pb-6 border-b border-green-50">
            <h2 className="text-2xl font-black text-green-950">
              {tr(lang, "profile.title") || "Personal Information"}
            </h2>
            {!isEditing ? (
              <button 
                className="flex items-center gap-2 px-5 py-2.5 bg-green-50 text-green-700 font-bold rounded-xl hover:bg-green-100 transition-colors border border-green-200"
                onClick={() => { setIsEditing(true); setMessage(""); setError("") }}
              >
                <Edit3 className="h-4 w-4" /> Edit Details
              </button>
            ) : (
              <button 
                className="flex items-center gap-2 px-5 py-2.5 bg-gray-50 text-gray-700 font-bold rounded-xl hover:bg-gray-100 transition-colors border border-gray-200"
                onClick={() => setIsEditing(false)}
              >
                <X className="h-4 w-4" /> Cancel
              </button>
            )}
          </div>

          {message && (
            <div className="bg-green-50 text-green-700 text-sm font-semibold rounded-2xl p-4 border border-green-200 flex items-center gap-3 mb-6">
              <span className="flex-shrink-0 w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
              {message}
            </div>
          )}

          {error && (
            <div className="bg-red-50 text-red-600 text-sm font-semibold rounded-2xl p-4 border border-red-100 flex items-center gap-3 mb-6">
              <span className="flex-shrink-0 w-2 h-2 rounded-full bg-red-500"></span>
              {error}
            </div>
          )}

          {!isEditing ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-y-6 gap-x-12">
              {Object.entries(FIELD_LABELS).filter(([key]) => key !== 'name' && key !== 'email').map(([key, label]) => (
                <div key={key} className="flex flex-col">
                  <span className="text-green-800/60 text-sm font-bold mb-1 uppercase tracking-wider">{label}</span>
                  <span className="text-green-950 font-bold text-lg">
                    {displayValue(key, user[key])}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <form onSubmit={handleSave} className="space-y-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                <InputField label={tr(lang, "profile.fullName")} name="name" />
                <InputField label={tr(lang, "profile.age")} name="age" type="number" />
                <InputField label={tr(lang, "profile.state")} name="location" />
                <InputField label={tr(lang, "profile.district")} name="area" />
                <SelectField label={tr(lang, "profile.caste")} name="caste" options={["General", "OBC", "SC", "ST"]} />
                <InputField label={tr(lang, "profile.income")} name="annual_income" type="number" />
                <SelectField label={tr(lang, "profile.gender")} name="gender" options={["Male", "Female", "Other"]} />
                
                <SelectField label={tr(lang, "profile.language")} name="language_pref" options={[
                  {label: "Hindi", value: "hi"}, {label: "English", value: "en"}, {label: "Tamil", value: "ta"}, 
                  {label: "Telugu", value: "te"}, {label: "Bengali", value: "bn"}, {label: "Marathi", value: "mr"}
                ]} />
              </div>

              <div className="flex items-center gap-3 mt-4 bg-green-50 p-4 rounded-2xl border border-green-100 w-fit">
                <input 
                  type="checkbox" id="pwd" name="pwd_status" 
                  checked={form.pwd_status} onChange={setField} 
                  className="w-5 h-5 text-green-600 bg-white border-green-300 rounded focus:ring-green-500 focus:ring-2"
                />
                <label htmlFor="pwd" className="text-sm font-bold text-green-900 cursor-pointer">
                  {tr(lang, "profile.pwd")} (Person with Disability)
                </label>
              </div>

              <div className="pt-6 border-t border-green-50 flex justify-end gap-4">
                <button type="button" onClick={() => setIsEditing(false)} className="px-6 py-3 bg-white text-green-800 font-bold rounded-xl hover:bg-green-50 transition-colors border border-green-200">
                  Cancel
                </button>
                <button type="submit" disabled={saving} className="flex items-center gap-2 bg-gradient-to-r from-green-600 to-emerald-500 text-white px-8 py-3 rounded-xl font-bold transition-all shadow-md hover:shadow-lg hover:-translate-y-0.5 active:scale-95 disabled:opacity-70">
                  <Save className="h-5 w-5" />
                  {saving ? tr(lang, "profile.saving") : tr(lang, "profile.save")}
                </button>
              </div>
            </form>
          )}
        </div>

      </div>
    </div>
  )
}