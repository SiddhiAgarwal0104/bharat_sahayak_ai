// src/pages/SearchResults.jsx
// Drop-in replacement / enhancement for Search.jsx
// Matches the exact design language of Dashboard.jsx

import { useState, useEffect } from "react"
import { useLocation, useNavigate } from "react-router-dom"
import { queryText } from "../api/api"
import { useAuth } from "../context/AuthContext"
import VoiceInput from "../components/ui/VoiceInput"
import { tr } from "../utils/i18n"
import {
  Search, Sparkles, Star, ArrowRight, ShieldCheck,
  Loader2, RotateCcw, ChevronRight, BookOpen, FileText
} from "lucide-react"

// Category colours matching your existing SchemeDetail.jsx
const CATEGORY_META = {
  health:      { bg: "bg-red-100",    text: "text-red-800",    dot: "bg-red-500"    },
  agriculture: { bg: "bg-green-100",  text: "text-green-800",  dot: "bg-green-500"  },
  pension:     { bg: "bg-amber-100",  text: "text-amber-800",  dot: "bg-amber-500"  },
  women:       { bg: "bg-pink-100",   text: "text-pink-800",   dot: "bg-pink-500"   },
  education:   { bg: "bg-blue-100",   text: "text-blue-800",   dot: "bg-blue-500"   },
  other:       { bg: "bg-gray-100",   text: "text-gray-700",   dot: "bg-gray-400"   },
}

const getSchemeImage = (name = "", category = "") => {
  const t = (name + " " + category).toLowerCase()
  if (t.includes("farm") || t.includes("kisan") || t.includes("krishi") || t.includes("agriculture"))
    return "/images/agriculture.jpg"
  if (t.includes("health") || t.includes("ayushman") || t.includes("medical"))
    return "/images/health.jpg"
  if (t.includes("pension") || t.includes("atal") || t.includes("nps") || t.includes("old age"))
    return "/images/pension.jpg"
  if (t.includes("women") || t.includes("mahila") || t.includes("beti") || t.includes("woman"))
    return "/images/women.jpg"
  if (t.includes("education") || t.includes("scholar") || t.includes("vidya"))
    return "/images/education.jpg"
  return "/images/home.jpg"
}

// ── Single scheme result card ─────────────────────────────────────────────────
function SchemeResultCard({ scheme, index, lang, navigate }) {
  const cat    = (scheme.category || "other").toLowerCase()
  const meta   = CATEGORY_META[cat] || CATEGORY_META.other
  const isBest = scheme.is_best_match || index === 0
  const score  = scheme.match_score ? Math.min(Math.round(scheme.match_score * 100), 99) : null

  return (
    <div className={`group relative bg-white rounded-[2.5rem] overflow-hidden shadow-[0_10px_30px_rgba(22,163,74,0.08)] hover:shadow-[0_20px_50px_rgba(22,163,74,0.2)] transition-all duration-500 border flex flex-col ${isBest ? "border-green-300" : "border-green-100"}`}>

      {/* Best match banner */}
      {isBest && (
        <div className="absolute top-0 left-0 right-0 z-20 bg-gradient-to-r from-green-600 to-emerald-500 text-white text-xs font-black uppercase tracking-widest py-2.5 text-center flex items-center justify-center gap-2">
          <Star className="h-3.5 w-3.5 fill-white" />
          Best Match for You
          <Star className="h-3.5 w-3.5 fill-white" />
        </div>
      )}

      {/* Image */}
      <div className={`relative overflow-hidden h-[200px] ${isBest ? "mt-[38px]" : ""} bg-green-50`}>
        <div className="absolute inset-0 bg-green-900/10 group-hover:bg-transparent transition-colors duration-500 z-10 mix-blend-overlay" />
        <img
          src={getSchemeImage(scheme.name, scheme.category)}
          alt={scheme.name}
          className="w-full h-full object-cover transform scale-100 group-hover:scale-110 transition-transform duration-700 ease-in-out"
        />
        {/* Category badge */}
        <div className="absolute top-4 left-4 z-20">
          <span className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-black uppercase tracking-widest bg-white/95 backdrop-blur-md shadow-md border border-green-50 text-green-900`}>
            <span className={`h-2 w-2 rounded-full ${meta.dot} animate-pulse`} />
            {scheme.category || "General"}
          </span>
        </div>
        {/* Match score badge */}
        {score && (
          <div className="absolute top-4 right-4 z-20">
            <span className="inline-flex items-center gap-1 px-3 py-1.5 rounded-xl text-xs font-black bg-white/95 backdrop-blur-md shadow-md border border-green-50 text-green-700">
              <Sparkles className="h-3 w-3 text-green-500" />
              {score}% match
            </span>
          </div>
        )}
        {/* Bottom fade */}
        <div className="absolute bottom-0 left-0 right-0 h-12 bg-gradient-to-t from-white to-transparent z-10" />
      </div>

      {/* Content */}
      <div className="px-6 pb-6 pt-4 flex-1 flex flex-col">
        <h3 className="text-xl font-black text-gray-900 mb-2 leading-tight group-hover:text-green-700 transition-colors">
          {scheme.name}
        </h3>
        <p className="text-gray-600 text-sm leading-relaxed mb-4 flex-1 line-clamp-3">
          {scheme.description || "A government initiative designed to support eligible beneficiaries."}
        </p>

        {/* Benefits chip */}
        {scheme.benefits && (
          <div className="mb-4 px-3 py-2 bg-green-50 border border-green-100 rounded-xl">
            <p className="text-[11px] font-black text-green-600 uppercase tracking-widest mb-0.5">Benefit</p>
            <p className="text-sm font-semibold text-green-900 line-clamp-2">{scheme.benefits}</p>
          </div>
        )}

        {/* Action buttons */}
        <div className="flex gap-3 pt-4 border-t border-green-50">
          <button
            onClick={() => navigate(`/scheme/${scheme.id}`)}
            className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-white border-2 border-green-200 text-green-700 rounded-2xl font-bold hover:bg-green-50 transition-all text-sm"
          >
            <BookOpen className="h-4 w-4" />
            Explain
          </button>
          <button
            onClick={() => navigate(`/scheme/${scheme.id}/form`)}
            className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-br from-green-600 to-emerald-600 text-white rounded-2xl font-bold transition-all duration-300 shadow-[0_6px_16px_rgba(22,163,74,0.3)] hover:shadow-[0_10px_22px_rgba(22,163,74,0.4)] hover:-translate-y-0.5 active:scale-95 text-sm"
          >
            Apply
            <span className="bg-white/20 p-1 rounded-full group-hover/btn:translate-x-1 transition-transform">
              <ArrowRight className="h-3.5 w-3.5" />
            </span>
          </button>
        </div>
      </div>
    </div>
  )
}

// ── Main page ─────────────────────────────────────────────────────────────────
export default function SearchResults() {
  const { user }   = useAuth()
  const navigate   = useNavigate()
  const location   = useLocation()
  const lang       = user?.language_pref || "en"

  const [textQuery, setTextQuery] = useState(location.state?.query || "")
  const [schemes,   setSchemes]   = useState([])
  const [intent,    setIntent]    = useState(null)
  const [loading,   setLoading]   = useState(false)
  const [error,     setError]     = useState(null)
  const [searched,  setSearched]  = useState(false)

  // Auto-search if navigated with a query
  useEffect(() => {
    if (location.state?.query) search(location.state.query)
  }, [location.state?.query])

  const search = async (query) => {
    if (!query?.trim()) return
    setLoading(true); setError(null); setSearched(true)
    try {
      const res = await queryText(query, lang)
      setSchemes(res.data.schemes || [])
      setIntent(res.data.intent || null)
    } catch {
      setError("Search failed. Please try again.")
    } finally { setLoading(false) }
  }

  const handleSubmit = (e) => { e.preventDefault(); search(textQuery) }
  const handleVoice  = ({ text }) => { setTextQuery(text); search(text) }

  return (
    <div className="bg-[#f0fdf4] min-h-screen pb-20 pt-[100px] relative">

      {/* Background blobs */}
      <div className="absolute top-0 left-0 w-full h-[400px] bg-gradient-to-b from-green-100 to-[#f0fdf4] pointer-events-none z-0" />
      <div className="absolute top-20 right-10 w-[400px] h-[400px] bg-emerald-300/20 rounded-full blur-[120px] pointer-events-none z-0" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 space-y-10">

        {/* ── Search header card ─────────────────────────────────────────── */}
        <div className="bg-white/80 backdrop-blur-xl rounded-[2.5rem] p-8 md:p-10 shadow-[0_20px_60px_-15px_rgba(22,163,74,0.15)] border border-white">
          <div className="flex items-center gap-3 mb-2">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-green-100 to-emerald-100 border border-green-200 text-green-800 text-xs font-black uppercase tracking-widest">
              <Sparkles className="h-4 w-4 text-green-600" />
              AI-Powered Search
            </div>
          </div>
          <h1 className="text-3xl md:text-4xl font-black text-green-950 mb-6 tracking-tight">
            Find Your Scheme
          </h1>

          {/* Text search */}
          <form onSubmit={handleSubmit} className="flex gap-3 mb-4">
            <div className="relative flex-1 group">
              <div className="absolute inset-y-0 left-0 pl-5 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-green-600/50 group-focus-within:text-green-600 transition-colors" />
              </div>
              <input
                type="text"
                value={textQuery}
                onChange={(e) => setTextQuery(e.target.value)}
                placeholder={tr(lang, "search.placeholder") || "e.g. pension for senior citizens, health insurance..."}
                className="w-full pl-12 pr-5 py-4 bg-white border-2 border-green-100 rounded-2xl focus:outline-none focus:border-green-500 focus:ring-4 focus:ring-green-500/20 transition-all font-medium text-green-950 placeholder-green-800/40 shadow-sm"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-green-600 to-green-500 hover:from-green-700 hover:to-green-600 text-white rounded-2xl font-bold transition-all shadow-[0_8px_20px_rgba(22,163,74,0.3)] hover:shadow-[0_12px_25px_rgba(22,163,74,0.4)] hover:-translate-y-0.5 disabled:opacity-70"
            >
              {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : <><Search className="h-5 w-5" /> Search</>}
            </button>
          </form>

          {/* Voice input */}
          <div className="flex items-center gap-3">
            <span className="text-sm font-bold text-green-700">Or speak:</span>
            <VoiceInput onResult={handleVoice} language={lang} />
          </div>
        </div>

        {/* ── Loading ────────────────────────────────────────────────────── */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-20 text-green-600">
            <div className="relative mb-6">
              <div className="w-20 h-20 rounded-full bg-green-100 flex items-center justify-center">
                <Sparkles className="h-10 w-10 text-green-500 animate-pulse" />
              </div>
              <div className="absolute inset-0 rounded-full border-4 border-green-300 border-t-green-600 animate-spin" />
            </div>
            <h3 className="text-2xl font-bold text-green-950">Finding best schemes...</h3>
            <p className="text-green-700 mt-2">Analysing your profile and query</p>
          </div>
        )}

        {/* ── Error ─────────────────────────────────────────────────────── */}
        {error && !loading && (
          <div className="bg-red-50 border border-red-200 rounded-3xl p-8 text-center">
            <p className="text-red-600 font-semibold mb-4">{error}</p>
            <button onClick={() => search(textQuery)} className="inline-flex items-center gap-2 px-6 py-3 bg-red-100 text-red-700 rounded-xl font-bold hover:bg-red-200 transition-colors">
              <RotateCcw className="h-4 w-4" /> Try Again
            </button>
          </div>
        )}

        {/* ── Results ───────────────────────────────────────────────────── */}
        {!loading && searched && !error && (
          <>
            {/* Result header */}
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div>
                <h2 className="text-2xl font-black text-green-950">
                  {schemes.length > 0 ? `Top ${schemes.length} Schemes Found` : "No schemes found"}
                </h2>
                {intent && (
                  <p className="text-green-700 mt-1 font-medium flex items-center gap-2">
                    Showing results for
                    <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-green-100 text-green-800 text-sm font-black rounded-full capitalize border border-green-200">
                      <span className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
                      {intent}
                    </span>
                  </p>
                )}
              </div>
              <button
                onClick={() => { setSearched(false); setSchemes([]); setTextQuery("") }}
                className="flex items-center gap-2 px-4 py-2 text-sm text-green-700 bg-green-50 border border-green-200 rounded-xl font-bold hover:bg-green-100 transition-colors"
              >
                <RotateCcw className="h-4 w-4" /> New Search
              </button>
            </div>

            {schemes.length === 0 ? (
              <div className="bg-white/60 backdrop-blur-md border border-green-100 rounded-3xl p-16 text-center shadow-lg">
                <div className="w-24 h-24 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                  <Search className="h-12 w-12 text-green-400" />
                </div>
                <h3 className="text-2xl font-black text-green-950 mb-3">No schemes found</h3>
                <p className="text-green-700 mb-6">Try a different query or browse by category</p>
                <button onClick={() => navigate("/dashboard")} className="bg-gradient-to-r from-green-600 to-green-500 text-white px-8 py-3 rounded-2xl font-bold shadow-lg hover:-translate-y-0.5 transition-all">
                  Back to Dashboard
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {schemes.slice(0, 3).map((scheme, idx) => (
                  <SchemeResultCard
                    key={scheme.id || idx}
                    scheme={scheme}
                    index={idx}
                    lang={lang}
                    navigate={navigate}
                  />
                ))}
              </div>
            )}
          </>
        )}

        {/* ── Empty state (before search) ───────────────────────────────── */}
        {!loading && !searched && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {["Health & Medical", "Pension & Retirement", "Agriculture & Farming", "Women Empowerment"].map((cat, i) => (
              <button
                key={i}
                onClick={() => { setTextQuery(cat); search(cat) }}
                className="bg-white/80 backdrop-blur-xl border border-green-100 rounded-2xl p-5 text-left hover:border-green-300 hover:shadow-lg transition-all group"
              >
                <p className="text-xs font-black text-green-600 uppercase tracking-widest mb-1">Quick Search</p>
                <p className="text-sm font-bold text-green-950 group-hover:text-green-700 transition-colors">{cat}</p>
                <ChevronRight className="h-4 w-4 text-green-400 mt-2 group-hover:translate-x-1 transition-transform" />
              </button>
            ))}
          </div>
        )}

      </div>
    </div>
  )
}
