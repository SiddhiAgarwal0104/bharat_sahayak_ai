// src/hooks/useVoice.js
import { useState, useRef } from "react"

export function useVoice() {
  const [recording,  setRecording]  = useState(false)
  const [audioBlob,  setAudioBlob]  = useState(null)
  const [error,      setError]      = useState(null)
  const mediaRef  = useRef(null)
  const chunksRef = useRef([])
  const blobResolveRef = useRef(null)

  const start = async () => {
    setError(null)
    setAudioBlob(null)
    blobResolveRef.current = null
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      
      // Use correct MIME type - MediaRecorder defaults to webm/opus
      // We'll let the backend handle any format since Whisper accepts multiple formats
      const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : 'audio/webm'
      
      const recorder = new MediaRecorder(stream, { mimeType })
      chunksRef.current = []

      recorder.ondataavailable = (e) => chunksRef.current.push(e.data)
      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: mimeType })
        console.log(`[Voice] Recording stopped, blob size: ${blob.size} bytes, MIME: ${mimeType}`)
        setAudioBlob(blob)
        // Resolve the promise if we're waiting for it
        if (blobResolveRef.current) {
          blobResolveRef.current(blob)
          blobResolveRef.current = null
        }
        stream.getTracks().forEach((t) => t.stop())
      }

      recorder.start()
      mediaRef.current = recorder
      setRecording(true)
      console.log("[Voice] Recording started")
    } catch (err) {
      console.error("[Voice] Error:", err)
      setError("Microphone access denied. Please allow mic access and try again.")
    }
  }

  const stop = () => {
    mediaRef.current?.stop()
    setRecording(false)
  }

  // Get the blob and wait for it to be ready
  const getBlob = () => {
    return new Promise((resolve) => {
      if (audioBlob) {
        resolve(audioBlob)
      } else {
        blobResolveRef.current = resolve
      }
    })
  }

  const reset = () => {
    setAudioBlob(null)
    setError(null)
  }

  return { recording, audioBlob, error, start, stop, reset, getBlob }
}