// src/pages/SchemeDetail.jsx
// Explain scheme page — matches Dashboard.jsx green design system exactly

import { useEffect, useState, useRef } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { getScheme } from "../api/api"
import { useAuth } from "../context/AuthContext"
import { tr } from "../utils/i18n"
import {
  ArrowLeft, ShieldCheck, Sparkles, CheckCircle2, XCircle,
  FileText, ExternalLink, Loader2, AlertCircle,
  IndianRupee, Users, Calendar, BookOpen, ArrowRight, Star,
  Volume2, VolumeX, Play, Square
} from "lucide-react"

const CATEGORY_META = {
  health:      { bg: "bg-red-100",   text: "text-red-800",   dot: "bg-red-500",   border: "border-red-200"   },
  agriculture: { bg: "bg-green-100", text: "text-green-800", dot: "bg-green-500", border: "border-green-200" },
  pension:     { bg: "bg-amber-100", text: "text-amber-800", dot: "bg-amber-500", border: "border-amber-200" },
  women:       { bg: "bg-pink-100",  text: "text-pink-800",  dot: "bg-pink-500",  border: "border-pink-200"  },
  education:   { bg: "bg-blue-100",  text: "text-blue-800",  dot: "bg-blue-500",  border: "border-blue-200"  },
  other:       { bg: "bg-gray-100",  text: "text-gray-700",  dot: "bg-gray-400",  border: "border-gray-200"  },
}

const LANG_LABEL = {
  hi: "Hindi", en: "English", ta: "Tamil",
  te: "Telugu", bn: "Bengali", mr: "Marathi",
}

const getSchemeImage = (name = "", category = "") => {
  const t = (name + " " + category).toLowerCase()
  if (t.includes("farm") || t.includes("kisan") || t.includes("krishi"))
    return "https://images.pexels.com/photos/10327341/pexels-photo-10327341.jpeg?auto=compress&cs=tinysrgb&w=800"
  if (t.includes("health") || t.includes("ayushman") || t.includes("medical"))
    return "https://images.pexels.com/photos/4386466/pexels-photo-4386466.jpeg?auto=compress&cs=tinysrgb&w=800"
  if (t.includes("pension") || t.includes("atal") || t.includes("nps"))
    return "https://images.pexels.com/photos/3823488/pexels-photo-3823488.jpeg?auto=compress&cs=tinysrgb&w=800"
  if (t.includes("women") || t.includes("mahila") || t.includes("beti"))
    return "https://images.pexels.com/photos/3768911/pexels-photo-3768911.jpeg?auto=compress&cs=tinysrgb&w=800"
  return "https://images.pexels.com/photos/1598075/pexels-photo-1598075.jpeg?auto=compress&cs=tinysrgb&w=800"
}

function checkEligibility(user, criteria) {
  if (!criteria || !user) return []
  const checks = []
  if (criteria.min_age)
    checks.push({ label: `Age ${criteria.min_age}+`, pass: Number(user.age) >= criteria.min_age })
  if (criteria.max_age)
    checks.push({ label: `Age below ${criteria.max_age}`, pass: Number(user.age) <= criteria.max_age })
  if (criteria.max_income)
    checks.push({ label: `Annual income ≤ ₹${criteria.max_income.toLocaleString()}`, pass: Number(user.annual_income) <= criteria.max_income })
  if (criteria.gender)
    checks.push({ label: criteria.gender === "F" ? "For women only" : "For men only", pass: user.gender === criteria.gender })
  if (criteria.caste && criteria.caste.length > 0)
    checks.push({ label: `Caste: ${criteria.caste.join(", ")}`, pass: criteria.caste.includes(user.caste) })
  if (criteria.pwd_only)
    checks.push({ label: "Person with disability", pass: Boolean(user.pwd_status) })
  return checks
}

// ── Voice Player Hook ────────────────────────────────────────────────────────
function useVoicePlayer(schemeId, lang) {
  const audioRef        = useRef(null)
  const [state, setState] = useState("idle")   // "idle" | "loading" | "playing" | "error"

  // Cleanup on unmount
  useEffect(() => () => {
    if (audioRef.current) {
      audioRef.current.pause()
      URL.revokeObjectURL(audioRef.current.src)
    }
  }, [])

  const play = async () => {
    // If already playing, stop it
    if (state === "playing" && audioRef.current) {
      audioRef.current.pause()
      audioRef.current.currentTime = 0
      setState("idle")
      return
    }

    // If audio already loaded, just replay
    if (audioRef.current && state === "idle") {
      try {
        await audioRef.current.play()
        setState("playing")
        return
      } catch (_) { /* fall through to re-fetch */ }
    }

    setState("loading")
    try {
      const token = localStorage.getItem("token")
      const backendUrl = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000"
      const res = await fetch(
        `${backendUrl}/schemes/${schemeId}/voice?lang=${lang}`,
        { headers: { Authorization: `Bearer ${token}` } }
      )
      if (!res.ok) throw new Error(`HTTP ${res.status}`)

      const blob    = await res.blob()
      const blobUrl = URL.createObjectURL(blob)

      // Revoke old object URL if any
      if (audioRef.current) URL.revokeObjectURL(audioRef.current.src)

      const audio = new Audio(blobUrl)
      audioRef.current = audio

      audio.onended = () => setState("idle")
      audio.onerror = () => setState("error")

      await audio.play()
      setState("playing")
    } catch (e) {
      console.error("[VoicePlayer] fetch/play error:", e)
      setState("error")
    }
  }

  const stop = () => {
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current.currentTime = 0
    }
    setState("idle")
  }

  return { state, play, stop }
}

// ── Voice Button Component ───────────────────────────────────────────────────
function VoiceButton({ schemeId, lang }) {
  const { state, play } = useVoicePlayer(schemeId, lang)
  const langLabel = LANG_LABEL[lang] || "Hindi"

  const label = {
    idle:    `Listen in ${langLabel}`,
    loading: "Generating audio…",
    playing: "Stop audio",
    error:   "Audio unavailable — retry",
  }[state]

  const Icon = state === "playing" ? Square
             : state === "loading" ? Loader2
             : state === "error"   ? VolumeX
             : Volume2

  const colorClass = state === "error"
    ? "bg-red-50 border-red-200 text-red-700 hover:bg-red-100"
    : state === "playing"
    ? "bg-green-600 border-green-600 text-white hover:bg-green-700"
    : "bg-white border-green-200 text-green-700 hover:bg-green-50 hover:-translate-y-0.5"

  return (
    <button
      onClick={play}
      disabled={state === "loading"}
      title={label}
      className={`flex items-center justify-center gap-2 px-6 py-4 border-2 rounded-2xl font-bold transition-all disabled:opacity-60 disabled:cursor-not-allowed ${colorClass}`}
    >
      <Icon className={`h-5 w-5 flex-shrink-0 ${state === "loading" ? "animate-spin" : ""}`} />
      <span className="whitespace-nowrap">{label}</span>
    </button>
  )
}

// ── Main Page ────────────────────────────────────────────────────────────────
export default function SchemeDetail() {
  const { id }   = useParams()
  const { user } = useAuth()
  const navigate = useNavigate()
  const lang     = user?.language_pref || "en"

  const [scheme,      setScheme]      = useState(null)
  const [loading,     setLoading]     = useState(true)
  const [error,       setError]       = useState(null)
  const [translated,  setTranslated]  = useState(null)   // translated fields from Gemini
  const [translating, setTranslating] = useState(false)  // spinner while Gemini works

  // Helper: pick translated text if available, else fall back to English
  const t = (field) => translated?.[field] || scheme?.[field] || ""

  useEffect(() => {
    getScheme(id)
      .then(r => setScheme(r.data))
      .catch(() => setError("Could not load scheme. Please try again."))
      .finally(() => setLoading(false))
  }, [id])

  // Fetch Gemini translation whenever scheme loads and language is not English
  useEffect(() => {
    if (!scheme || lang === "en") return
    const token = localStorage.getItem("token")
    setTranslating(true)
    fetch(`${import.meta.env.VITE_BACKEND_URL || "http://localhost:8000"}/schemes/${scheme.id}/translate?lang=${lang}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(r => r.json())
      .then(data => { if (data.translated) setTranslated(data) })
      .catch(e => console.warn("[SchemeDetail] translation fetch failed:", e))
      .finally(() => setTranslating(false))
  }, [scheme, lang])

  if (loading) return (
    <div className="min-h-screen bg-[#f0fdf4] pt-[100px] flex items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <Loader2 className="h-12 w-12 text-green-600 animate-spin" />
        <p className="text-green-800 font-semibold">Loading scheme details...</p>
      </div>
    </div>
  )

  if (error || !scheme) return (
    <div className="min-h-screen bg-[#f0fdf4] pt-[100px] px-4">
      <div className="max-w-2xl mx-auto">
        <div className="bg-red-50 border border-red-200 rounded-3xl p-10 text-center">
          <AlertCircle className="h-12 w-12 text-red-400 mx-auto mb-4" />
          <p className="text-red-600 font-semibold mb-4">{error || "Scheme not found"}</p>
          <button onClick={() => navigate(-1)} className="px-6 py-3 bg-white border-2 border-red-200 text-red-700 rounded-xl font-bold hover:bg-red-50 transition-colors">
            ← Go Back
          </button>
        </div>
      </div>
    </div>
  )

  const cat     = (scheme.category || "other").toLowerCase()
  const meta    = CATEGORY_META[cat] || CATEGORY_META.other
  const checks  = checkEligibility(user, scheme.eligibility_criteria)
  const allPass = checks.length > 0 && checks.every(c => c.pass)
  const docs    = t("docs_needed")
    ? t("docs_needed").split(/[,\n]/).map(d => d.trim()).filter(Boolean)
    : []

  return (
    <div className="bg-[#f0fdf4] min-h-screen pb-20 pt-[100px] relative">

      {/* Background */}
      <div className="absolute top-0 left-0 w-full h-[400px] bg-gradient-to-b from-green-100 to-[#f0fdf4] pointer-events-none z-0" />
      <div className="absolute top-20 right-10 w-[400px] h-[400px] bg-emerald-300/20 rounded-full blur-[120px] pointer-events-none z-0" />

      <div className="max-w-5xl mx-auto px-4 sm:px-6 relative z-10 space-y-8">

        {/* Back */}
        <button onClick={() => navigate(-1)} className="inline-flex items-center gap-2 text-green-700 font-bold hover:text-green-900 transition-colors">
          <ArrowLeft className="h-5 w-5" /> Back
        </button>

        {/* ── Hero Card ─────────────────────────────────────────────────── */}
        <div className="bg-white/80 backdrop-blur-xl rounded-[2.5rem] overflow-hidden shadow-[0_20px_60px_-15px_rgba(22,163,74,0.15)] border border-white">

          {/* Hero image */}
          <div className="relative h-[260px] overflow-hidden">
            <img src={getSchemeImage(scheme.name, scheme.category)} alt={scheme.name} className="w-full h-full object-cover" />
            <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent" />

            {/* Badges on image */}
            <div className="absolute bottom-6 left-6 right-6 flex items-end justify-between">
              <div>
                <span className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-black uppercase tracking-widest bg-white/95 backdrop-blur-md ${meta.text} mb-3`}>
                  <span className={`h-2 w-2 rounded-full ${meta.dot}`} />
                  {scheme.category}
                </span>
                <h1 className="text-2xl md:text-3xl font-black text-white leading-tight max-w-xl drop-shadow-lg">
                  {scheme.name}
                </h1>
              </div>
              {allPass && (
                <div className="flex-shrink-0 bg-green-500 text-white px-4 py-2 rounded-2xl font-black text-sm flex items-center gap-2 shadow-lg">
                  <CheckCircle2 className="h-4 w-4" /> Eligible
                </div>
              )}
            </div>
          </div>

          {/* Description */}
          <div className="p-8 md:p-10">
            {/* Translating indicator */}
            {translating && (
              <div className="flex items-center gap-2 mb-4 text-sm text-green-700 font-semibold">
                <Loader2 className="h-4 w-4 animate-spin" />
                Translating to {LANG_LABEL[lang] || lang}...
              </div>
            )}
            <p className="text-gray-700 leading-relaxed text-lg mb-8">
              {t("description")}
            </p>

            {/* Three action buttons — Apply, Official Portal, Voice */}
            <div className="flex flex-col sm:flex-row gap-4">
              <button
                onClick={() => navigate(`/scheme/${scheme.id}/form`)}
                className="flex-1 flex items-center justify-center gap-3 px-8 py-4 bg-gradient-to-r from-green-600 to-emerald-500 hover:from-green-700 hover:to-emerald-600 text-white rounded-2xl font-bold text-lg transition-all shadow-[0_8px_20px_rgba(22,163,74,0.3)] hover:shadow-[0_12px_25px_rgba(22,163,74,0.4)] hover:-translate-y-0.5 active:scale-95"
              >
                <FileText className="h-5 w-5" />
                Start Guided Application
                <span className="bg-white/20 p-1.5 rounded-full">
                  <ArrowRight className="h-4 w-4" />
                </span>
              </button>

              {/* ── Voice Button ── */}
              <VoiceButton schemeId={scheme.id} lang={lang} />

              {scheme.form_url && (
                <a
                  href={scheme.form_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-center gap-2 px-6 py-4 bg-white border-2 border-green-200 text-green-700 rounded-2xl font-bold hover:bg-green-50 hover:-translate-y-0.5 transition-all"
                >
                  <ExternalLink className="h-5 w-5" />
                  Official Portal
                </a>
              )}
            </div>
          </div>
        </div>

        {/* ── Info grid ─────────────────────────────────────────────────── */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

          {/* Benefits */}
          {scheme.benefits && (
            <div className="bg-white/80 backdrop-blur-xl rounded-[2.5rem] p-8 shadow-[0_10px_30px_rgba(22,163,74,0.08)] border border-white">
              <div className="flex items-center gap-3 mb-4">
                <div className="h-12 w-12 rounded-2xl bg-gradient-to-br from-green-100 to-emerald-50 border border-green-200 flex items-center justify-center">
                  <IndianRupee className="h-6 w-6 text-green-600" />
                </div>
                <h2 className="text-xl font-black text-green-950">Benefits</h2>
              </div>
              <div className="bg-green-50 border border-green-100 rounded-2xl p-4">
                <p className="text-green-900 font-semibold leading-relaxed">{t("benefits")}</p>
              </div>
            </div>
          )}

          {/* Eligibility */}
          {checks.length > 0 && (
            <div className="bg-white/80 backdrop-blur-xl rounded-[2.5rem] p-8 shadow-[0_10px_30px_rgba(22,163,74,0.08)] border border-white">
              <div className="flex items-center gap-3 mb-4">
                <div className="h-12 w-12 rounded-2xl bg-gradient-to-br from-green-100 to-emerald-50 border border-green-200 flex items-center justify-center">
                  <ShieldCheck className="h-6 w-6 text-green-600" />
                </div>
                <div>
                  <h2 className="text-xl font-black text-green-950">Eligibility</h2>
                  <p className="text-sm text-green-700 font-medium">
                    {allPass ? "✓ You qualify for this scheme" : "Some criteria not met"}
                  </p>
                </div>
              </div>
              <div className="space-y-3">
                {checks.map((c, i) => (
                  <div key={i} className={`flex items-center gap-3 p-3 rounded-xl border ${c.pass ? "bg-green-50 border-green-100" : "bg-red-50 border-red-100"}`}>
                    {c.pass
                      ? <CheckCircle2 className="h-5 w-5 text-green-600 flex-shrink-0" />
                      : <XCircle className="h-5 w-5 text-red-400 flex-shrink-0" />
                    }
                    <span className={`text-sm font-semibold ${c.pass ? "text-green-900" : "text-red-700 line-through"}`}>
                      {c.label}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Documents */}
          {docs.length > 0 && (
            <div className="bg-white/80 backdrop-blur-xl rounded-[2.5rem] p-8 shadow-[0_10px_30px_rgba(22,163,74,0.08)] border border-white md:col-span-2">
              <div className="flex items-center gap-3 mb-6">
                <div className="h-12 w-12 rounded-2xl bg-gradient-to-br from-amber-100 to-yellow-50 border border-amber-200 flex items-center justify-center">
                  <BookOpen className="h-6 w-6 text-amber-600" />
                </div>
                <h2 className="text-xl font-black text-green-950">Documents Required</h2>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                {docs.map((doc, i) => (
                  <div key={i} className="flex items-center gap-3 p-4 bg-amber-50 border border-amber-100 rounded-2xl">
                    <div className="h-8 w-8 rounded-xl bg-amber-100 flex items-center justify-center flex-shrink-0">
                      <FileText className="h-4 w-4 text-amber-700" />
                    </div>
                    <span className="text-sm font-semibold text-amber-900">{doc}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* ── Apply CTA ─────────────────────────────────────────────────── */}
        <div className="bg-gradient-to-r from-green-600 to-emerald-600 rounded-[2.5rem] p-8 md:p-10 flex flex-col md:flex-row items-center justify-between gap-6 shadow-[0_20px_60px_-15px_rgba(22,163,74,0.4)]">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Sparkles className="h-5 w-5 text-white/80" />
              <span className="text-white/80 text-sm font-bold uppercase tracking-widest">AI-Guided Application</span>
            </div>
            <h3 className="text-2xl md:text-3xl font-black text-white mb-2">Ready to apply?</h3>
            <p className="text-white/80 font-medium">Our AI will guide you field by field in your language.</p>
          </div>
          <button
            onClick={() => navigate(`/scheme/${scheme.id}/form`)}
            className="flex-shrink-0 flex items-center gap-3 px-8 py-4 bg-white text-green-700 rounded-2xl font-black text-lg hover:bg-green-50 hover:-translate-y-0.5 active:scale-95 transition-all shadow-lg"
          >
            Start Now
            <span className="bg-green-100 p-1.5 rounded-full">
              <ArrowRight className="h-5 w-5" />
            </span>
          </button>
        </div>

      </div>
    </div>
  )
}