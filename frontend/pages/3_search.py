import streamlit as st

from components.voice_recorder import render_voice_recorder


if not st.session_state.get("token"):
	st.warning("Please login first, then come back to this page.")
	if st.button("Go to Register"):
		st.switch_page("pages/1_register.py")
	st.stop()

st.title("STT and Voice Recorder Test")
st.caption("Record your voice, verify transcript, then press Send.")

payload = render_voice_recorder("Tap and speak for 3-6 seconds")

if payload:
	st.success("Voice payload captured.")
	st.write("Detected payload type:", payload.get("type"))
	st.write("Detected language:", payload.get("language", "en"))

	if payload.get("type") == "text":
		st.subheader("Final query text")
		st.write(payload.get("content", ""))
	else:
		st.info("Unedited transcript path selected. Audio bytes will be used downstream.")
		st.write("Audio size (bytes):", len(payload.get("content", b"")))
