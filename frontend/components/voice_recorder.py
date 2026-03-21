# frontend/components/voice_recorder.py
# Member 3 imports render_voice_recorder() into their search page.
import streamlit as st
import requests, os
from audio_recorder_streamlit import audio_recorder

BACKEND = os.getenv("BACKEND_URL", "http://localhost:8000")

def render_voice_recorder(label: str = "Tap to speak") -> dict | None:
    """
    Renders mic widget. Returns {'type':'audio'|'text','content':bytes|str} or None.
    Usage: from frontend.components.voice_recorder import render_voice_recorder
    """
    token       = st.session_state.get("token", "")
    lang_hint   = st.session_state.get("language", "hi")
    if not token:
        st.warning("Please login first to test STT.")
        return None

    st.markdown(f"**{label}**")
    audio_bytes = audio_recorder(text="", recording_color="#e53935",
                                  neutral_color="#1a3a5c", icon_size="2x", pause_threshold=2.0)

    if not audio_bytes:
        return None

    st.audio(audio_bytes, format="audio/wav")

    with st.spinner("Transcribing..."):
        try:
            res      = requests.post(f"{BACKEND}/stt/transcribe",
                         files={"audio": ("rec.wav", audio_bytes, "audio/wav")},
                         data={"language_hint": lang_hint},
                         headers={"Authorization": f"Bearer {token}"}, timeout=30)
            if res.status_code != 200:
                st.error(f"STT failed ({res.status_code}): {res.text}")
                return None

            data     = res.json()
            transcript = data.get("text", "")
            language   = data.get("language", "en")
        except Exception as e:
            st.error(f"STT request error: {e}")
            transcript, language = "", "en"

    edited = st.text_area("Transcript (edit if needed)", value=transcript,
                           height=80, label_visibility="visible")

    if st.button("Send", key="voice_send_btn"):
        if edited.strip() != transcript.strip():
            return {"type": "text", "content": edited.strip(), "language": language}
        return {"type": "audio", "content": audio_bytes, "language": language}

    return None