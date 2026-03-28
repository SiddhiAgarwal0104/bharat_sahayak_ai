import { useState, useEffect } from "react"
import { useLocation } from "react-router-dom"
import { queryText } from "../api/api"
import { useAuth } from "../context/AuthContext"
import VoiceInput from "../components/ui/VoiceInput"
import SchemeCard from "../components/ui/SchemeCard"
import { tr } from "../utils/i18n"

export default function Search() {
  const { user } = useAuth()
  const location = useLocation()
  const language  = user?.language_pref || "hi"

  const [textQuery, setTextQuery] = useState(location.state?.query || "")
  const [schemes,   setSchemes]   = useState([])
  const [intent,    setIntent]    = useState(null)
  const [loading,   setLoading]   = useState(false)
  const [error,     setError]     = useState(null)
  const [searched,  setSearched]  = useState(false)

  // Auto-search if coming from landing page voice search
  useEffect(() => {
    if (location.state?.query) {
      search(location.state.query, language)
    }
  }, [location.state?.query, language])

  const search = async (query, lang) => {
    if (!query.trim()) {
      console.warn("[Search] Empty query")
      return
    }
    console.log(`[Search] Searching for: "${query}" (language: ${lang})`)
    setLoading(true); setError(null); setSearched(true)
    try {
      const res = await queryText(query, lang)
      console.log(`[Search] ✅ Got ${res.data.schemes?.length || 0} schemes`)
      setSchemes(res.data.schemes || [])
      setIntent(res.data.intent || null)
    } catch (err) {
      console.error("[Search] ❌ Error:", err)
      setError(tr(language, "search.error"))
    } finally { setLoading(false) }
  }

  const handleText = (e) => {
    e.preventDefault()
    console.log("[Search] Text form submitted")
    search(textQuery, language)
  }

  const handleVoiceResult = ({ text, language: lang }) => {
    console.log(`[Search] Voice result: "${text}" (${lang})`)
    setTextQuery(text)
    search(text, lang)
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">

      <h1 className="text-2xl font-bold text-neutral-900 mb-2">Search schemes</h1>
      <p className="text-neutral-700 mb-8">{tr(language, "search.subtitle")}</p>

      {/* Voice input */}
      <div className="card mb-6">
        <h2 className="text-lg font-semibold mb-4">🎤 {tr(language, "search.speakQuery")}</h2>
        <VoiceInput onResult={handleVoiceResult} language={language} />
      </div>

      {/* Text input */}
      <div className="card mb-8">
        <h2 className="text-lg font-semibold mb-4">⌨️ {tr(language, "search.typeQuery")}</h2>
        <form onSubmit={handleText} className="flex gap-3">
          <input
            value={textQuery}
            onChange={(e) => setTextQuery(e.target.value)}
            className="input-field flex-1"
            placeholder={tr(language, "search.placeholder")}
          />
          <button type="submit" disabled={loading} className="btn-primary px-6">
            {loading ? "..." : tr(language, "search.searchBtn")}
          </button>
        </form>
      </div>

      {/* Results */}
      {loading && (
        <div className="flex justify-center py-12">
          <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin"/>
        </div>
      )}

      {error && (
        <div className="bg-danger/10 text-danger rounded-xl p-4 text-center mb-6">{error}</div>
      )}

      {!loading && searched && (
        <>
          {intent && (
            <div className="flex items-center gap-2 mb-4">
              <span className="text-neutral-700 text-sm">{tr(language, "search.showingFor")}</span>
              <span className="badge bg-primary text-white capitalize">{intent}</span>
            </div>
          )}

          {schemes.length === 0 ? (
            <div className="card text-center py-12">
              <p className="text-neutral-700">{tr(language, "search.none")}</p>
            </div>
          ) : (
            <div className="space-y-4">
              <p className="text-sm text-neutral-700">{tr(language, "search.count", { count: schemes.length })}</p>
              {schemes.map((s, i) => (
                <SchemeCard key={s.id} scheme={s} isBestMatch={i === 0} />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  )
}