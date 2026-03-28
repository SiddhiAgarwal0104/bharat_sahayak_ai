// src/pages/FormPage.jsx
// Apply guidance page — matches Dashboard.jsx green design system exactly

import { useState, useEffect } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { useAuth } from "../context/AuthContext"
import VoiceInput from "../components/ui/VoiceInput"
import { tr } from "../utils/i18n"
import {
  ChevronLeft, ChevronRight, Loader2, CheckCircle2, AlertCircle,
  FileText, ExternalLink, Lightbulb, ArrowLeft, Star,
  Sparkles, ShieldCheck, BookOpen
} from "lucide-react"

// ── API helpers ───────────────────────────────────────────────────────────────
const API = async (url, opts = {}) => {
  const token = localStorage.getItem("token")
  const res   = await fetch(url, {
    ...opts,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(opts.headers || {}),
    },
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

const startFormSession  = (schemeId) => API(`/api/form/${schemeId}/start`, { method: "POST" })
const getFormStep       = (schemeId, sessionId, n) => API(`/api/form/${schemeId}/step/${n}?session_id=${sessionId}`)
const advanceFormStep   = (schemeId, sessionId) => API(`/api/form/${schemeId}/next`, { method: "POST", body: JSON.stringify({ session_id: sessionId }) })
const completeFormSession = (schemeId, sessionId) => API(`/api/form/${schemeId}/complete`, { method: "POST", body: JSON.stringify({ session_id: sessionId }) })

// ── Step dot indicator ────────────────────────────────────────────────────────
function StepDots({ total, current }) {
  const dots = Math.min(total, 8)
  return (
    <div className="flex items-center gap-1.5">
      {Array.from({ length: dots }, (_, i) => (
        <div key={i} className={`rounded-full transition-all duration-300 ${i < current ? "h-2.5 w-2.5 bg-green-500" : i === current - 1 ? "h-3 w-3 bg-green-600" : "h-2 w-2 bg-green-200"}`} />
      ))}
      {total > 8 && <span className="text-xs text-green-600 font-bold ml-1">+{total - 8}</span>}
    </div>
  )
}

// ── Completion screen ─────────────────────────────────────────────────────────
function CompletionScreen({ schemeName, formUrl, navigate, lang }) {
  return (
    <div className="min-h-screen bg-[#f0fdf4] pt-[100px] pb-20 px-4">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white/80 backdrop-blur-xl rounded-[2.5rem] p-8 md:p-12 shadow-[0_20px_60px_-15px_rgba(22,163,74,0.15)] border border-white text-center">
          {/* Success animation */}
          <div className="relative inline-flex mb-8">
            <div className="absolute inset-0 rounded-full bg-green-400 blur-xl opacity-30 animate-pulse" />
            <div className="w-24 h-24 bg-gradient-to-br from-green-400 to-emerald-600 rounded-full flex items-center justify-center relative shadow-lg">
              <CheckCircle2 className="h-12 w-12 text-white" />
            </div>
          </div>

          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-green-100 border border-green-200 text-green-800 text-xs font-black uppercase tracking-widest mb-4">
            <Sparkles className="h-3.5 w-3.5" /> Guidance Complete
          </div>

          <h1 className="text-3xl md:text-4xl font-black text-green-950 mb-4">
            All Fields Guided!
          </h1>
          <p className="text-lg text-green-800/80 mb-8 max-w-md mx-auto leading-relaxed">
            You have been guided through every field of the <strong>{schemeName}</strong> form. Now submit it on the official portal.
          </p>

          {/* Steps summary */}
          <div className="bg-green-50 border border-green-100 rounded-2xl p-6 text-left mb-8">
            <p className="text-sm font-black text-green-700 uppercase tracking-widest mb-3">What to do next</p>
            {[
              "Open the official portal link below",
              "Fill in the values exactly as guided",
              "Upload the documents you have ready",
              "Submit and note your application reference number",
            ].map((step, i) => (
              <div key={i} className="flex items-start gap-3 mb-2 last:mb-0">
                <span className="flex-shrink-0 h-6 w-6 rounded-full bg-green-200 text-green-800 text-xs font-black flex items-center justify-center">{i + 1}</span>
                <p className="text-sm font-semibold text-green-900">{step}</p>
              </div>
            ))}
          </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            {formUrl && (
              <a
                href={formUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center justify-center gap-2 px-8 py-4 bg-gradient-to-r from-green-600 to-emerald-500 text-white rounded-2xl font-bold text-lg shadow-[0_8px_20px_rgba(22,163,74,0.3)] hover:shadow-[0_12px_25px_rgba(22,163,74,0.4)] hover:-translate-y-0.5 transition-all"
              >
                <ExternalLink className="h-5 w-5" />
                Open Official Form
              </a>
            )}
            <button
              onClick={() => navigate("/dashboard")}
              className="flex items-center justify-center gap-2 px-8 py-4 bg-white border-2 border-green-200 text-green-700 rounded-2xl font-bold hover:bg-green-50 transition-all"
            >
              Back to Dashboard
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

// ── Main FormPage ─────────────────────────────────────────────────────────────
export default function FormPage() {
  const { schemeId } = useParams()
  const { user }     = useAuth()
  const navigate     = useNavigate()
  const lang         = user?.language_pref || "en"

  const [sessionId,    setSessionId]    = useState(null)
  const [currentStep,  setCurrentStep]  = useState(null)
  const [stepNumber,   setStepNumber]   = useState(1)
  const [totalSteps,   setTotalSteps]   = useState(10)
  const [fieldValue,   setFieldValue]   = useState("")
  const [loading,      setLoading]      = useState(true)
  const [submitting,   setSubmitting]   = useState(false)
  const [completed,    setCompleted]    = useState(false)
  const [error,        setError]        = useState(null)
  const [schemeInfo,   setSchemeInfo]   = useState({})

  const progressPct = totalSteps > 0 ? Math.round((stepNumber / totalSteps) * 100) : 0

  useEffect(() => {
    if (!schemeId || !user) return
    const init = async () => {
      try {
        const res = await startFormSession(schemeId)
        setSessionId(res.session_id)
        setTotalSteps(res.total_fields || 10)
        setSchemeInfo(res.scheme || {})
        const first = await getFormStep(schemeId, res.session_id, 1)
        setCurrentStep(first)
        // Pre-fill if available
        if (first?.prefilled_value) setFieldValue(String(first.prefilled_value))
      } catch (e) {
        setError("Could not load form. Please try again.")
      } finally { setLoading(false) }
    }
    init()
  }, [schemeId, user])

  const handleNext = async () => {
    if (!fieldValue.trim()) { setError("Please enter a value before continuing."); return }
    setSubmitting(true); setError(null)
    try {
      const res = await advanceFormStep(schemeId, sessionId)
      if (res.completed) {
        setCompleted(true)
      } else {
        setCurrentStep(res)
        setStepNumber(s => s + 1)
        setFieldValue(res?.prefilled_value ? String(res.prefilled_value) : "")
      }
    } catch (e) { setError(e.message) }
    finally { setSubmitting(false) }
  }

  const handleComplete = async () => {
    setSubmitting(true)
    try { await completeFormSession(schemeId, sessionId); setCompleted(true) }
    catch (e) { setError(e.message) }
    finally { setSubmitting(false) }
  }

  // ── States ──────────────────────────────────────────────────────────────────
  if (loading) return (
    <div className="min-h-screen bg-[#f0fdf4] pt-[100px] flex items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <div className="relative">
          <div className="w-20 h-20 rounded-full bg-green-100 flex items-center justify-center">
            <BookOpen className="h-10 w-10 text-green-500" />
          </div>
          <div className="absolute inset-0 rounded-full border-4 border-green-300 border-t-green-600 animate-spin" />
        </div>
        <p className="text-green-800 font-semibold">Preparing your guided form...</p>
      </div>
    </div>
  )

  if (completed) return (
    <CompletionScreen
      schemeName={schemeInfo.name || ""}
      formUrl={schemeInfo.form_url || schemeInfo.application_url || ""}
      navigate={navigate}
      lang={lang}
    />
  )

  // ── Main form guidance UI ───────────────────────────────────────────────────
  return (
    <div className="bg-[#f0fdf4] min-h-screen pb-20 pt-[100px] relative">

      {/* Background */}
      <div className="absolute top-0 left-0 w-full h-[400px] bg-gradient-to-b from-green-100 to-[#f0fdf4] pointer-events-none z-0" />
      <div className="absolute top-20 right-10 w-[400px] h-[400px] bg-emerald-300/20 rounded-full blur-[120px] pointer-events-none z-0" />

      <div className="max-w-6xl mx-auto px-4 sm:px-6 relative z-10 space-y-6">

        {/* Back */}
        <button onClick={() => navigate(-1)} className="inline-flex items-center gap-2 text-green-700 font-bold hover:text-green-900 transition-colors">
          <ArrowLeft className="h-5 w-5" /> Back to scheme
        </button>

        {/* ── Page header ─────────────────────────────────────────────── */}
        <div className="bg-white/80 backdrop-blur-xl rounded-[2.5rem] p-6 md:p-8 shadow-[0_20px_60px_-15px_rgba(22,163,74,0.15)] border border-white">
          <div className="flex items-center gap-3 mb-1">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-gradient-to-r from-green-100 to-emerald-100 border border-green-200 text-green-800 text-xs font-black uppercase tracking-widest">
              <Sparkles className="h-3.5 w-3.5 text-green-600" />
              AI Form Guide
            </div>
          </div>
          <h1 className="text-2xl md:text-3xl font-black text-green-950 tracking-tight">
            {schemeInfo.name || "Scheme Application"}
          </h1>
          <p className="text-green-700 font-medium mt-1">
            Follow each step — we guide you field by field in your language
          </p>
        </div>

        {/* ── Two-column layout ─────────────────────────────────────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

          {/* LEFT — Main guidance column */}
          <div className="lg:col-span-2 space-y-6">

            {/* Progress card */}
            <div className="bg-white/80 backdrop-blur-xl rounded-[2.5rem] p-6 md:p-8 shadow-[0_20px_60px_-15px_rgba(22,163,74,0.15)] border border-white">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <p className="text-xs font-black text-green-600 uppercase tracking-widest mb-1">
                    Step {stepNumber} of {totalSteps}
                  </p>
                  <h2 className="text-xl md:text-2xl font-black text-green-950">Field-by-Field Guidance</h2>
                </div>
                <div className="text-right">
                  <p className="text-4xl font-black text-green-600 leading-none">{progressPct}%</p>
                  <p className="text-xs text-green-700 font-semibold mt-1">complete</p>
                </div>
              </div>

              {/* Progress bar */}
              <div className="w-full bg-green-100/50 rounded-full h-3 overflow-hidden mb-3">
                <div
                  className="bg-gradient-to-r from-green-500 to-emerald-500 h-full rounded-full transition-all duration-700"
                  style={{ width: `${progressPct}%` }}
                />
              </div>
              <StepDots total={totalSteps} current={stepNumber} />
            </div>

            {/* Field card */}
            {currentStep && (
              <div className="bg-white/80 backdrop-blur-xl rounded-[2.5rem] p-6 md:p-8 shadow-[0_20px_60px_-15px_rgba(22,163,74,0.15)] border border-white space-y-6">

                {/* Field name + required */}
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <span className="inline-flex items-center justify-center h-8 w-8 rounded-xl bg-green-100 text-green-700 text-sm font-black">{stepNumber}</span>
                    <h3 className="text-xl md:text-2xl font-black text-green-950">
                      {currentStep.field_name}
                      {currentStep.required && <span className="text-red-500 ml-1">*</span>}
                    </h3>
                  </div>
                  {/* Instruction — in user's language */}
                  <p className="text-gray-700 leading-relaxed text-base pl-10">
                    {lang === "hi"
                      ? currentStep.instruction_hi || currentStep.instruction_en || currentStep.instruction
                      : currentStep.instruction_en || currentStep.instruction}
                  </p>
                </div>

                {/* Pre-fill highlight */}
                {currentStep.can_prefill && currentStep.prefilled_value && (
                  <div className="flex items-start gap-3 p-4 bg-green-50 border-2 border-green-200 rounded-2xl">
                    <CheckCircle2 className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-xs font-black text-green-600 uppercase tracking-widest mb-0.5">Auto-filled from your profile</p>
                      <p className="text-green-900 font-bold text-lg">{currentStep.prefilled_value}</p>
                    </div>
                  </div>
                )}

                {/* Text input */}
                <div className="space-y-3">
                  <label className="block text-sm font-bold text-green-900">
                    {currentStep.can_prefill ? "Confirm or edit value:" : "Enter value:"}
                  </label>
                  <input
                    type="text"
                    value={fieldValue}
                    onChange={e => setFieldValue(e.target.value)}
                    placeholder="Type here..."
                    className="w-full px-5 py-4 bg-white border-2 border-green-100 rounded-2xl text-green-950 placeholder-green-800/40 focus:outline-none focus:border-green-500 focus:ring-4 focus:ring-green-500/20 transition-all font-medium shadow-sm text-lg"
                  />

                  {/* Voice input */}
                  <div className="pt-1">
                    <p className="text-sm font-bold text-green-700 mb-2">Or speak your answer:</p>
                    <VoiceInput onResult={({ text }) => setFieldValue(text)} language={lang} />
                  </div>
                </div>

                {/* Error */}
                {error && (
                  <div className="flex items-center gap-3 p-4 bg-red-50 border border-red-100 rounded-2xl text-red-600">
                    <AlertCircle className="h-5 w-5 flex-shrink-0" />
                    <p className="text-sm font-semibold">{error}</p>
                  </div>
                )}

                {/* Nav buttons */}
                <div className="flex gap-4 pt-2">
                  <button
                    disabled={stepNumber === 1 || submitting}
                    onClick={() => { setStepNumber(s => s - 1); setError(null) }}
                    className="flex items-center justify-center gap-2 px-6 py-3.5 bg-white border-2 border-green-200 text-green-700 rounded-2xl font-bold hover:bg-green-50 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
                  >
                    <ChevronLeft className="h-5 w-5" /> Back
                  </button>

                  <button
                    disabled={!fieldValue.trim() || submitting}
                    onClick={stepNumber === totalSteps ? handleComplete : handleNext}
                    className="flex-1 flex items-center justify-center gap-2 px-6 py-3.5 bg-gradient-to-r from-green-600 to-emerald-500 hover:from-green-700 hover:to-emerald-600 text-white rounded-2xl font-bold disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-[0_8px_20px_rgba(22,163,74,0.3)] hover:shadow-[0_12px_25px_rgba(22,163,74,0.4)] hover:-translate-y-0.5 active:scale-95 text-lg"
                  >
                    {submitting ? (
                      <Loader2 className="h-5 w-5 animate-spin" />
                    ) : (
                      <>
                        {stepNumber === totalSteps ? "Complete" : "Next Field"}
                        <span className="bg-white/20 p-1.5 rounded-full">
                          <ChevronRight className="h-4 w-4" />
                        </span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* RIGHT — Sidebar */}
          <div className="space-y-5">

            {/* Document needed */}
            {currentStep?.document_needed && (
              <div className="bg-amber-50 backdrop-blur-xl rounded-[2.5rem] p-6 shadow-[0_10px_30px_rgba(22,163,74,0.08)] border-2 border-amber-200">
                <div className="flex items-center gap-3 mb-3">
                  <div className="h-10 w-10 rounded-xl bg-amber-100 flex items-center justify-center">
                    <AlertCircle className="h-5 w-5 text-amber-600" />
                  </div>
                  <p className="font-black text-amber-900">Document Needed</p>
                </div>
                <p className="text-sm font-bold text-amber-800">
                  {typeof currentStep.document_needed === "object"
                    ? currentStep.document_needed.name
                    : currentStep.document_needed}
                </p>
                <p className="text-xs text-amber-700 mt-1">Keep this document open and ready</p>
              </div>
            )}

            {/* Government link */}
            {(schemeInfo.form_url || schemeInfo.application_url) && (
              <div className="bg-blue-50 backdrop-blur-xl rounded-[2.5rem] p-6 shadow-[0_10px_30px_rgba(22,163,74,0.08)] border-2 border-blue-200">
                <div className="flex items-center gap-3 mb-3">
                  <div className="h-10 w-10 rounded-xl bg-blue-100 flex items-center justify-center">
                    <ExternalLink className="h-5 w-5 text-blue-600" />
                  </div>
                  <p className="font-black text-blue-900">Official Form</p>
                </div>
                <p className="text-xs text-blue-700 mb-3 font-medium">Open in a new tab. This guide follows the exact field order on that page.</p>
                <a
                  href={schemeInfo.form_url || schemeInfo.application_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold transition-all text-sm w-full justify-center"
                >
                  <ExternalLink className="h-4 w-4" />
                  Open Form Tab
                </a>
              </div>
            )}

            {/* Tips */}
            <div className="bg-white/80 backdrop-blur-xl rounded-[2.5rem] p-6 shadow-[0_10px_30px_rgba(22,163,74,0.08)] border border-white">
              <div className="flex items-center gap-2 mb-4">
                <Lightbulb className="h-5 w-5 text-amber-500" />
                <h3 className="font-black text-green-950">Tips</h3>
              </div>
              <ul className="space-y-2.5">
                {[
                  "Keep your Aadhaar card nearby",
                  "Have your bank passbook open",
                  "Use the same name as on Aadhaar",
                  "Screenshot each completed field",
                  "Do not close the form tab between steps",
                ].map((tip, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-green-800">
                    <span className="h-5 w-5 rounded-full bg-green-100 text-green-600 flex items-center justify-center flex-shrink-0 text-xs font-black mt-0.5">{i + 1}</span>
                    {tip}
                  </li>
                ))}
              </ul>
            </div>

            {/* Progress summary */}
            <div className="bg-gradient-to-br from-green-600 to-emerald-700 rounded-[2.5rem] p-6 shadow-[0_10px_30px_rgba(22,163,74,0.3)]">
              <div className="flex items-center gap-2 mb-4">
                <ShieldCheck className="h-5 w-5 text-white/80" />
                <p className="text-white/80 text-sm font-black uppercase tracking-widest">Your Progress</p>
              </div>
              <div className="flex items-baseline gap-2 mb-3">
                <span className="text-5xl font-black text-white">{stepNumber}</span>
                <span className="text-white/60 text-lg font-bold">/ {totalSteps}</span>
              </div>
              <p className="text-white/80 text-sm font-medium">fields guided so far</p>
              <div className="mt-4 w-full bg-white/20 rounded-full h-2">
                <div className="bg-white rounded-full h-2 transition-all duration-700" style={{ width: `${progressPct}%` }} />
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  )
}
