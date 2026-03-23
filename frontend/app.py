# frontend/app.py — temp version (Member 4 owns final)
import streamlit as st

st.set_page_config(page_title="SahayakAI", page_icon="🇮🇳", layout="wide")

# --- existing keys ---
st.session_state.setdefault("token", None)
st.session_state.setdefault("user_id", None)
st.session_state.setdefault("user_name", None)
st.session_state.setdefault("language", "hi")

# --- ADD: keys needed for scheme detail + form guide features ---
st.session_state.setdefault("selected_scheme", None)
st.session_state.setdefault("explanation", "")
st.session_state.setdefault("explanation_audio", None)   # bytes of MP3 for scheme-level audio
st.session_state.setdefault("apply_scheme_id", None)
st.session_state.setdefault("apply_scheme_url", "")
st.session_state.setdefault("form_session_id", None)
st.session_state.setdefault("form_step", None)
st.session_state.setdefault("field_explanations", {})    # cache for per-field audio {field_key: data}

with st.sidebar:
    st.markdown("## 🇮🇳 SahayakAI")
    st.divider()
    if st.session_state["token"]:
        st.success(f"Hi, {st.session_state.get('user_name','')}")
        if st.button("Logout", use_container_width=True):
            # --- CHANGE: also clear the new keys on logout ---
            st.session_state.update({
                "token": None,
                "user_id": None,
                "user_name": None,
                "selected_scheme": None,
                "explanation": "",
                "explanation_audio": None,
                "apply_scheme_id": None,
                "apply_scheme_url": "",
                "form_session_id": None,
                "form_step": None,
                "field_explanations": {},
            })
            st.rerun()
    else:
        st.info("Not logged in")

if not st.session_state["token"]:
    st.title("Welcome to SahayakAI 🇮🇳")
    st.markdown("Your guide to government schemes and benefits.")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📝 Register", use_container_width=True, type="primary"):
            st.switch_page("pages/1_register.py")
    with c2:
        if st.button("🔑 Login", use_container_width=True):
            st.switch_page("pages/login.py")
else:
    st.switch_page("pages/2_home.py")