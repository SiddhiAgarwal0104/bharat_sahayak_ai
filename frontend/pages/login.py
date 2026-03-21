# frontend/pages/login.py
import streamlit as st
import requests, os

BACKEND = os.getenv("BACKEND_URL", "http://localhost:8000")

if st.session_state.get("token"):
    st.switch_page("pages/2_home.py")

st.title("Login to SahayakAI")

with st.form("login"):
    email    = st.text_input("Email")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Login", use_container_width=True)

if submitted:
    if not email or not password:
        st.error("Please enter email and password")
    else:
        with st.spinner("Logging in..."):
            try:
                r = requests.post(f"{BACKEND}/auth/login",
                    json={"email": email.strip(), "password": password}, timeout=10)
                if r.status_code == 200:
                    d = r.json()
                    st.session_state.update({
                        "token": d["access_token"],
                        "user_id": d["user_id"],
                        "user_name": d["name"],
                    })
                    st.switch_page("pages/2_home.py")
                else:
                    st.error("Incorrect email or password")
            except requests.exceptions.ConnectionError:
                st.error("Cannot reach backend. Is it running?")

st.divider()
if st.button("New user? Register"):
    st.switch_page("pages/1_register.py")