# frontend/pages/1_register.py
import streamlit as st
import requests, os

BACKEND = os.getenv("BACKEND_URL", "http://localhost:8000")

if st.session_state.get("token"):
    st.switch_page("pages/2_home.py")

st.title("Create your profile")
st.caption("Fill in your details to get personalised scheme recommendations")

with st.form("reg"):
    c1, c2 = st.columns(2)
    with c1:
        name     = st.text_input("Full Name *")
        age      = st.number_input("Age *", min_value=1, max_value=120, value=25)
        gender   = st.selectbox("Gender *", ["Male","Female","Other"])
        email    = st.text_input("Email *")
        password = st.text_input("Password *", type="password")
    with c2:
        location = st.selectbox("State *", [
            "Andhra Pradesh","Assam","Bihar","Chhattisgarh","Delhi","Goa","Gujarat",
            "Haryana","Himachal Pradesh","Jharkhand","Karnataka","Kerala",
            "Madhya Pradesh","Maharashtra","Odisha","Punjab","Rajasthan",
            "Tamil Nadu","Telangana","Uttar Pradesh","Uttarakhand","West Bengal"])
        area     = st.text_input("District / Area *")
        caste    = st.selectbox("Caste Category *", ["General","OBC","SC","ST"])
        income   = st.number_input("Annual Income (₹) *", min_value=0, value=120000, step=1000)
        pwd      = st.selectbox("Person with Disability?", ["No","Yes"])
        lang     = st.selectbox("Preferred Language *",
                    ["Hindi","English","Tamil","Telugu","Bengali","Marathi","Gujarati","Punjabi"])
    submitted = st.form_submit_button("Create Account", use_container_width=True)

if submitted:
    lang_map   = {"Hindi":"hi","English":"en","Tamil":"ta","Telugu":"te",
                  "Bengali":"bn","Marathi":"mr","Gujarati":"gu","Punjabi":"pa"}
    gender_map = {"Male":"M","Female":"F","Other":"O"}

    errors = []
    if not name.strip():  errors.append("Name is required")
    if not email.strip(): errors.append("Email is required")
    if len(password) < 8: errors.append("Password must be at least 8 characters")
    if not area.strip():  errors.append("District is required")

    if errors:
        for e in errors: st.error(e)
    else:
        with st.spinner("Creating account..."):
            try:
                r = requests.post(f"{BACKEND}/auth/register", json={
                    "name": name.strip(), "age": int(age),
                    "location": location, "area": area.strip(),
                    "caste": caste, "annual_income": float(income),
                    "gender": gender_map[gender], "pwd_status": pwd == "Yes",
                    "language_pref": lang_map[lang],
                    "email": email.strip(), "password": password,
                }, timeout=10)

                if r.status_code == 201:
                    lr = requests.post(f"{BACKEND}/auth/login",
                         json={"email": email.strip(), "password": password}, timeout=10)
                    if lr.status_code == 200:
                        d = lr.json()
                        st.session_state.update({
                            "token": d["access_token"], "user_id": d["user_id"],
                            "user_name": d["name"], "language": lang_map[lang],
                        })
                        st.success(f"Welcome, {name.split()[0]}!")
                        st.switch_page("pages/2_home.py")
                elif r.status_code == 400:
                    st.error("Email already registered. Please login.")
                else:
                    st.error(f"Error: {r.text}")
            except requests.exceptions.ConnectionError:
                st.error("Cannot reach backend. Is it running on port 8000?")

st.divider()
if st.button("Already have an account? Login"):
    st.switch_page("pages/login.py")