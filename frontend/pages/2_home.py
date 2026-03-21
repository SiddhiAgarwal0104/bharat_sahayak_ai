# frontend/pages/2_home.py — PLACEHOLDER (Member 2 replaces this)
import streamlit as st

if not st.session_state.get("token"):
    st.switch_page("pages/1_register.py")

st.title(f"Welcome, {st.session_state.get('user_name', 'User')}! 🎉")
st.info("Home dashboard is being built by Member 2.")