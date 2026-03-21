# frontend/app.py — temp version (Member 4 owns final)
import streamlit as st

st.set_page_config(page_title="SahayakAI", page_icon="🇮🇳", layout="wide")

st.session_state.setdefault("token", None)
st.session_state.setdefault("user_id", None)
st.session_state.setdefault("user_name", None)
st.session_state.setdefault("language", "hi")

with st.sidebar:
    st.markdown("## 🇮🇳 SahayakAI")
    st.divider()
    if st.session_state["token"]:
        st.success(f"Hi, {st.session_state.get('user_name','')}")
        if st.button("Logout", use_container_width=True):
            st.session_state.update({"token":None,"user_id":None,"user_name":None})
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