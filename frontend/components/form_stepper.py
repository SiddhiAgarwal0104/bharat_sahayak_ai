import streamlit as st
import tempfile
import os
import re

def render_stepper(step: dict):
    if not step:
        st.success("All fields complete! Go to the government website to submit.")
        return None

    current     = step.get("current_index", 0)
    total       = step.get("total_fields", 1)
    field_name  = step.get("field_name", "")
    instruction = step.get("instruction", "")
    prefilled   = step.get("prefilled_value")
    doc_needed  = step.get("document_needed")
    validation  = step.get("validation")
    is_required = step.get("is_required", True)

    # Progress
    pct = (current + 1) / max(total, 1)
    st.progress(pct, text=f"Field {current + 1} of {total}")
    st.markdown("---")

    # Field header
    req = " *(required)*" if is_required else " *(optional)*"
    st.markdown(f"### {field_name}{req}")

    # Instruction box — detailed
    st.info(instruction)

    # Audio button for instruction
    col_audio, col_space = st.columns([1, 3])
    with col_audio:
        if st.button("Listen", key=f"audio_{current}"):
            with st.spinner("Generating audio..."):
                try:
                    from gtts import gTTS
                    profile   = st.session_state.get("user_profile", {})
                    user_lang = profile.get("language_pref", "hi")
                    lang_map  = {
                        "hi": "hi", "en": "en", "ta": "ta",
                        "te": "te", "bn": "bn", "mr": "mr"
                    }
                    gtts_lang  = lang_map.get(user_lang, "hi")
                    clean_text = re.sub(r'\*\*|__|\*|_|#', '', instruction)
                    tts = gTTS(text=clean_text, lang=gtts_lang, slow=False)
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                    tts.save(tmp.name)
                    tmp.close()
                    with open(tmp.name, "rb") as f:
                        audio_bytes = f.read()
                    st.audio(audio_bytes, format="audio/mp3", autoplay=True)
                    os.unlink(tmp.name)
                except Exception as e:
                    st.error("Audio error: " + str(e))

    st.markdown("")

    # Document needed
    if doc_needed:
        st.warning("**Document needed:** " + doc_needed)

    # Validation hint
    if validation:
        st.caption("Format: " + validation)

    # Pre-filled value
    if prefilled:
        st.success("**Auto-filled from your profile:** " + prefilled)
        st.caption("Taken from your registration. Correct on the form if needed.")

    # Input box
    st.text_input(
        label       = "What you will type on the form:",
        value       = str(prefilled) if prefilled else "",
        placeholder = validation or "Enter value here",
        key         = f"field_input_{current}",
    )

    st.markdown("---")

    # Navigation
    left_col, right_col = st.columns(2)
    action = None

    with left_col:
        if current > 0:
            if st.button("Previous", key=f"back_{current}",
                         use_container_width=True):
                action = "back"

    with right_col:
        label = "Done" if current == total - 1 else "Next"
        if st.button(label, key=f"next_{current}",
                     use_container_width=True, type="primary"):
            action = "next"

    return action