// src/pages/SchemeDetail.jsx
import { useEffect, useState } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { getScheme } from "../api/api"
import { useAuth } from "../context/AuthContext"
import { tr } from "../utils/i18n"

const CATEGORY_COLORS = {
  education:   "bg-blue-100 text-blue-800",
  agriculture: "bg-green-100 text-green-800",
  health:      "bg-red-100 text-red-800",
  pension:     "bg-amber-100 text-amber-800",
  other:       "bg-gray-100 text-gray-700",
}

function EligibilityCheck({ label, pass }) {
  return (
    <div className="flex items-center gap-3 py-2 border-b border-neutral-100 last:border-0">
      <div className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0
                       ${pass ? "bg-success/20" : "bg-danger/20"}`}>
        <span className={`text-sm font-bold ${pass ? "text-success" : "text-danger"}`}>
          {pass ? "✓" : "✗"}
        </span>
      </div>
      <span className={`text-sm ${pass ? "text-neutral-900" : "text-neutral-500 line-through"}`}>
        {label}
      </span>
    </div>
  )
}

function checkEligibility(user, criteria) {
  if (!criteria || !user) return []
  const checks = []

  if (criteria.min_age)
    checks.push({ label: `Age ${criteria.min_age}+`, pass: user.age >= criteria.min_age })

  if (criteria.max_age)
    checks.push({ label: `Age below ${criteria.max_age}`, pass: user.age <= criteria.max_age })

  if (criteria.max_income)
    checks.push({
      label: `Annual income ≤ ₹${criteria.max_income.toLocaleString()}`,
      pass: user.annual_income <= criteria.max_income,
    })

  if (criteria.gender)
    checks.push({
      label: criteria.gender === "F" ? "For women only" : "For men only",
      pass: user.gender === criteria.gender,
    })

  if (criteria.caste && criteria.caste.length > 0)
    checks.push({
      label: `Caste: ${criteria.caste.join(", ")}`,
      pass: criteria.caste.includes(user.caste),
    })

  if (criteria.pwd_only)
    checks.push({
      label: "Person with disability",
      pass: user.pwd_status === true,
    })

  return checks
}

export default function SchemeDetail() {
  const { id }      = useParams()
  const { user }    = useAuth()
  const lang        = user?.language_pref || "en"
  const navigate    = useNavigate()
  const [scheme,  setScheme]  = useState(null)
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState(null)

  useEffect(() => {
    getScheme(id)
      .then((r) => setScheme(r.data))
      .catch(() => setError(tr(lang, "scheme.loadError")))
      .finally(() => setLoading(false))
  }, [id, lang])

  if (loading) return (
    <div className="flex justify-center py-20">
      <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin"/>
    </div>
  )

  if (error) return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <div className="bg-danger/10 text-danger rounded-xl p-4 text-center">{error}</div>
      <button onClick={() => navigate(-1)} className="btn-secondary w-full mt-4">{tr(lang, "scheme.goBack")}</button>
    </div>
  )

  if (!scheme) return null

  const eligibilityChecks = checkEligibility(user, scheme.eligibility_criteria)
  const allPass = eligibilityChecks.length > 0 && eligibilityChecks.every((c) => c.pass)
  const colorClass = CATEGORY_COLORS[scheme.category] || CATEGORY_COLORS.other

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 space-y-6">

      {/* Back button */}
      <button onClick={() => navigate(-1)}
              className="flex items-center gap-2 text-primary font-medium hover:underline">
        ← {tr(lang, "scheme.back")}
      </button>

      {/* Header card */}
      <div className="card">
        <div className="flex items-start justify-between gap-4 flex-wrap mb-4">
          <span className={`badge text-xs ${colorClass}`}>{scheme.category}</span>
          {allPass && (
            <span className="badge bg-success/20 text-success text-xs">
              ✓ {tr(lang, "scheme.eligible")}
            </span>
          )}
        </div>
        <h1 className="text-2xl font-bold text-neutral-900 mb-3">{scheme.name}</h1>
        <p className="text-neutral-700 leading-relaxed">{scheme.description}</p>
      </div>

      {/* Benefit amount */}
      {scheme.benefits && (
        <div className="card border-l-4 border-success">
          <p className="label text-success">{tr(lang, "scheme.benefit")}</p>
          <p className="text-xl font-bold text-success mt-1">{scheme.benefits}</p>
        </div>
      )}

      {/* Eligibility checklist */}
      {eligibilityChecks.length > 0 && (
        <div className="card">
          <h2 className="text-lg font-semibold mb-1">{tr(lang, "scheme.eligibilityCheck")}</h2>
          <p className="text-sm text-neutral-700 mb-4">
            {allPass ? tr(lang, "scheme.eligibilityPass") : tr(lang, "scheme.eligibilityFail")}
          </p>
          {eligibilityChecks.map((c, i) => (
            <EligibilityCheck key={i} label={c.label} pass={c.pass} />
          ))}
        </div>
      )}

      {/* Documents needed */}
      {scheme.docs_needed && (
        <div className="card">
          <h2 className="text-lg font-semibold mb-3">{tr(lang, "scheme.docs")}</h2>
          <ul className="space-y-2">
            {scheme.docs_needed.split(",").map((doc, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-neutral-700">
                <span className="text-primary mt-0.5 flex-shrink-0">•</span>
                {doc.trim()}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Apply section */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-2">{tr(lang, "scheme.applyTitle")}</h2>
        <p className="text-sm text-neutral-700 mb-4">
          {tr(lang, "scheme.applyText")}
        </p>
        <div className="flex gap-3 flex-wrap">
          {scheme.form_url ? (
            <a href={scheme.form_url} target="_blank" rel="noreferrer"
               className="btn-primary flex-1 text-center">
              {tr(lang, "scheme.applyBtn")}
            </a>
          ) : (
            <div className="bg-neutral-100 text-neutral-700 rounded-xl p-4 text-sm w-full text-center">
              {tr(lang, "scheme.noLink")}
            </div>
          )}
        </div>
      </div>

    </div>
  )
}