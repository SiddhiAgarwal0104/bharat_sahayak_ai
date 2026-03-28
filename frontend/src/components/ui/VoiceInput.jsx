// src/components/ui/VoiceInput.jsx
import { useState } from "react"
import { useVoice } from "../../hooks/useVoice"
import { queryAudio } from "../../api/api"

export default function VoiceInput({ onResult, language = "hi" }) {
  const { recording, audioBlob, error, start, stop, reset, getBlob } = useVoice()
  const [transcript, setTranscript]   = useState("")
  const [loading,    setLoading]      = useState(false)
  const [apiError,   setApiError]     = useState(null)

  const handleStop = async () => {
    stop()
    console.log("[VoiceInput] Stop button clicked, waiting for blob...")
    
    setLoading(true)
    setApiError(null)
    
    try {
      // Wait for blob to be ready
      const blob = await getBlob()
      if (!blob || blob.size === 0) {
        throw new Error("No audio recorded")
      }
      
      console.log(`[VoiceInput] Blob ready, size: ${blob.size} bytes, language: ${language}`)
      const res = await queryAudio(blob, language)
      
      const text = res.data?.text || ""
      console.log(`[VoiceInput] ✅ Transcription success: "${text.substring(0, 50)}..."`)
      setTranscript(text)
    } catch (err) {
      console.error("[VoiceInput] ❌ Error:", err.message)
      setApiError(err.message || "Could not transcribe audio. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  const handleSend = () => {
    if (transcript.trim()) {
      onResult({ text: transcript.trim(), language })
      setTranscript("")
      reset()
    }
  }

  return (
    <div className="space-y-4">

      {/* Mic button */}
      <div className="flex flex-col items-center gap-3">
        <button
          onClick={recording ? handleStop : start}
          className={`w-20 h-20 rounded-full flex items-center justify-center
                      transition-all shadow-lg active:scale-95 text-white font-bold
                      ${recording
                        ? "bg-danger animate-pulse scale-110"
                        : "bg-primary hover:bg-primary-dark"}`}
          aria-label={recording ? "Stop recording" : "Start recording"}>
          {recording ? (
            <svg width="28" height="28" fill="currentColor" viewBox="0 0 24 24">
              <rect x="6" y="6" width="12" height="12" rx="2"/>
            </svg>
          ) : (
            <svg width="28" height="28" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 1a4 4 0 0 1 4 4v7a4 4 0 0 1-8 0V5a4 4 0 0 1 4-4zm6 11a6 6 0 0 1-12 0H4a8 8 0 0 0 16 0h-2zm-6 9v-2"/>
            </svg>
          )}
        </button>
        <p className="text-sm text-neutral-700 font-medium">
          {recording ? "Recording... tap to stop" : "Tap mic to speak"}
        </p>
      </div>

      {/* Loading */}
      {loading && (
        <div className="flex items-center gap-2 justify-center text-neutral-700">
          <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin"/>
          <span className="text-sm">Transcribing...</span>
        </div>
      )}

      {/* Error */}
      {(error || apiError) && (
        <p className="text-danger text-sm text-center bg-danger/10 rounded-xl p-3">
          {error || apiError}
        </p>
      )}

      {/* Transcript edit */}
      {transcript && (
        <div className="space-y-3">
          <label className="label">Transcript — edit if needed</label>
          <textarea
            value={transcript}
            onChange={(e) => setTranscript(e.target.value)}
            rows={3}
            className="input-field resize-none"
            placeholder="Your speech will appear here..."
          />
          <div className="flex gap-3">
            <button onClick={handleSend} className="btn-primary flex-1">
              Search Schemes
            </button>
            <button onClick={() => { setTranscript(""); reset() }}
                    className="btn-secondary px-4">
              Clear
            </button>
          </div>
        </div>
      )}
    </div>
  )
}