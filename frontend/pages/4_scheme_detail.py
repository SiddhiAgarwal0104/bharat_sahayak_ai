import streamlit as st
import requests

BACKEND = "http://localhost:8000"

scheme = st.session_state.get("explain_scheme") or st.session_state.get("selected_scheme")
if not scheme:
    st.error("No scheme selected. Please go back and click on a scheme.")
    if st.button("Back to Search"):
        st.switch_page("pages/3_search.py")
    st.stop()

token   = st.session_state.get("token", "")
headers = {"Authorization": f"Bearer {token}"}
profile = st.session_state.get("user_profile", {})

scheme_name = scheme.get("name", "Scheme Detail")
scheme_cat  = scheme.get("category", "other")

st.title(scheme_name)
st.caption("Category: " + scheme_cat.title() + " Scheme")
st.markdown("---")

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("Benefits")
    st.success(scheme.get("benefits", "See official website for details."))
    st.subheader("About This Scheme")
    st.write(scheme.get("description", "No description available."))
    st.subheader("Documents Needed")
    docs = scheme.get("docs_needed", "")
    if docs:
        for doc in docs.split(","):
            st.write("- " + doc.strip())
    else:
        st.info("See official website for document requirements.")

with col2:
    st.subheader("Your Eligibility")
    criteria = scheme.get("eligibility_criteria") or {}
    if not criteria:
        st.info("Open to all citizens.")
    else:
        user_age    = profile.get("age", 0)
        user_income = profile.get("annual_income", 0)
        user_caste  = profile.get("caste", "")
        user_gender = profile.get("gender", "")
        user_pwd    = profile.get("pwd_status", False)
        checks = []
        if "min_age" in criteria and criteria["min_age"] is not None:
            ok = user_age >= criteria["min_age"]
            checks.append((ok, "Age " + str(criteria["min_age"]) + "+ years (you: " + str(user_age) + ")"))
        if "max_age" in criteria and criteria["max_age"] is not None:
            ok = user_age <= criteria["max_age"]
            checks.append((ok, "Age up to " + str(criteria["max_age"]) + " years"))
        if criteria.get("max_income"):
            ok = user_income <= criteria["max_income"]
            checks.append((ok, "Income below Rs." + str(criteria["max_income"])))
        if criteria.get("caste"):
            ok = user_caste in criteria["caste"]
            checks.append((ok, "Caste: " + ", ".join(criteria["caste"])))
        if criteria.get("gender"):
            ok = user_gender.lower().startswith(criteria["gender"].lower()[0])
            checks.append((ok, "Gender: " + criteria["gender"]))
        if criteria.get("pwd_only"):
            checks.append((user_pwd, "Person with Disability only"))
        for ok, label in checks:
            mark = "YES" if ok else "NO"
            st.write(mark + ": " + label)
        if checks and all(c[0] for c in checks):
            st.success("You meet all eligibility criteria!")
        elif checks:
            st.warning("You may not meet all criteria.")

st.markdown("---")
btn1, btn2, btn3 = st.columns([2, 2, 1])

with btn1:
    if st.button("Explain This Scheme", use_container_width=True, type="primary"):
        with st.spinner("Generating explanation..."):
            try:
                resp = requests.post(
                    BACKEND + "/form/query",
                    json={"action": "explain", "scheme": scheme,
                          "input_type": "text", "content": ""},
                    headers=headers, timeout=30
                )
                if resp.ok:
                    st.session_state["explanation"] = resp.json().get("text", "")
                    st.session_state["explanation_audio"] = None
                else:
                    st.error("Error " + str(resp.status_code) + ": " + resp.text)
            except Exception as e:
                st.error("Connection error: " + str(e))

with btn2:
    if st.button("Apply Now - Get Guidance", use_container_width=True):
        st.session_state["apply_scheme_id"]  = str(scheme.get("id", ""))
        st.session_state["apply_scheme_url"] = scheme.get("form_url", "")
        st.session_state["form_session_id"]  = None
        st.session_state["form_step"]        = None
        st.switch_page("pages/5_form_guide.py")

with btn3:
    if st.button("Back", use_container_width=True):
        st.switch_page("pages/3_search.py")

if st.session_state.get("explanation"):
    st.markdown("---")
    st.subheader("Explanation")
    st.markdown(st.session_state["explanation"])

    if st.button("Listen to Explanation"):
        with st.spinner("Generating audio..."):
            try:
                from gtts import gTTS
                import tempfile
                import os
                import re

                lang_map = {
                    "hi": "hi", "en": "en", "ta": "ta",
                    "te": "te", "bn": "bn", "mr": "mr"
                }
                user_lang  = profile.get("language_pref", "hi")
                gtts_lang  = lang_map.get(user_lang, "hi")
                clean_text = re.sub(r'\*\*|__|\*|_|#', '', st.session_state["explanation"])

                tts = gTTS(text=clean_text, lang=gtts_lang, slow=False)
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                tts.save(tmp.name)
                tmp.close()

                with open(tmp.name, "rb") as f:
                    audio_bytes = f.read()
                st.audio(audio_bytes, format="audio/mp3")
                os.unlink(tmp.name)

            except Exception as e:
                st.error("Could not generate audio: " + str(e))