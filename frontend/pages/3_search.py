# frontend/pages/3_search.py
# Member 3 owns this file
# Integrates Member 1's voice recorder and Member 2's NLP/profile endpoints

import streamlit as st
import requests
import os

BACKEND = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Find Schemes — BharatSahayakAI", layout="wide")

# ── Auth check ────────────────────────────────────────────────────────────────
token = st.session_state.get("token", "")
if not token:
    st.warning("Please login first.")
    if st.button("Go to Login"):
        st.switch_page("pages/login.py")
    st.stop()

headers = {"Authorization": f"Bearer {token}"}

# ── Import Member 3's scheme card ────────────────────────────────────────────
try:
    from components.scheme_card import show_scheme_card
except ImportError:
    def show_scheme_card(scheme, token=""):
        st.markdown(f"**{scheme.get('name')}**")
        st.caption(scheme.get("description", "")[:150])

st.title("Find Government Schemes")
st.caption("Search in English, Hindi, or any Indian language — type or speak")
st.divider()

# ── Input row — text + voice ──────────────────────────────────────────────────
col_input, col_voice = st.columns([4, 1])

voice_query = ""
with col_input:
    text_query = st.text_input(
        "Type your query",
        placeholder="e.g. health insurance for family, kisan subsidy, pension for old age",
        label_visibility="collapsed",
    )

with col_voice:
    # Use Member 1's voice recorder if available
    try:
        from components.voice_recorder import render_voice_recorder
        payload = render_voice_recorder("🎤 Speak")
        if payload and payload.get("type") == "text":
            voice_query = payload.get("content", "")
    except ImportError:
        if st.button("🎤 Voice\n(coming soon)"):
            st.info("Voice module from Member 1 not ready yet.")

# ── Category filter buttons ───────────────────────────────────────────────────
st.write("")
st.caption("Or browse by category:")
c1, c2, c3, c4, c5 = st.columns(5)
category_filter = st.session_state.get("category_filter", "")

with c1:
    if st.button("All",         use_container_width=True): st.session_state["category_filter"] = ""; category_filter = ""
with c2:
    if st.button("Health",      use_container_width=True): st.session_state["category_filter"] = "health"; category_filter = "health"
with c3:
    if st.button("Pension",     use_container_width=True): st.session_state["category_filter"] = "pension"; category_filter = "pension"
with c4:
    if st.button("Agriculture", use_container_width=True): st.session_state["category_filter"] = "agriculture"; category_filter = "agriculture"
with c5:
    if st.button("Women",       use_container_width=True): st.session_state["category_filter"] = "women"; category_filter = "women"

st.divider()
final_query = voice_query or text_query or category_filter

# ── Search ────────────────────────────────────────────────────────────────────
if final_query:
    with st.spinner("Finding best schemes for you..."):

        # Step 1: NLP intent — Member 2's endpoint
        try:
            nlp_resp  = requests.post(
                f"{BACKEND}/nlp/classify",
                json={"text": final_query, "language": "auto"},
                headers=headers, timeout=5,
            ).json()
            intent = nlp_resp.get("intent", category_filter or "")
            slots  = nlp_resp.get("slots", {})
        except Exception:
            intent   = category_filter or ""
            slots    = {}
            nlp_resp = {"query_text": final_query, "language": "en", "intent": intent, "slots": slots}

        # Step 2: Eligible candidates — Member 2's profile agent
        try:
            profile_resp  = requests.get(
                f"{BACKEND}/profile/eligible",
                params={"intent": intent},
                headers=headers, timeout=5,
            ).json()
            candidate_ids = profile_resp.get("scheme_ids", [])
        except Exception:
            candidate_ids = []

        # Step 3: Search — Member 3's endpoint
        try:
            search_resp = requests.post(
                f"{BACKEND}/schemes/search",
                json={"intent_obj": {
                    "query_text": final_query,
                    "language":   "en",
                    "intent":     intent,
                    "slots":      slots,
                }, "candidate_ids": candidate_ids},
                headers=headers, timeout=10,
            )
            schemes = search_resp.json()
        except Exception as e:
            st.error(f"Search failed: {e}")
            schemes = []

    # ── Show results ──────────────────────────────────────────────────────────
    if not schemes:
        st.info("No matching schemes found. Try a different query or browse by category.")
    else:
        if intent:
            st.markdown(
                f"Results for: <span style='background:#EEEDFE;color:#3D2A8A;"
                f"padding:2px 10px;border-radius:10px;font-size:12px;font-weight:600'>"
                f"{intent.upper()}</span>",
                unsafe_allow_html=True,
            )
        cols = st.columns(len(schemes))
        for i, scheme in enumerate(schemes):
            with cols[i]:
                show_scheme_card(scheme, token)

# ── Default — show recommended ────────────────────────────────────────────────
else:
    st.subheader("Recommended for you")
    with st.spinner("Loading recommendations..."):
        try:
            recommended = requests.get(
                f"{BACKEND}/schemes/recommended", headers=headers, timeout=10
            ).json()
        except Exception:
            recommended = []

    if recommended:
        cols = st.columns(min(len(recommended), 3))
        for i, scheme in enumerate(recommended[:3]):
            with cols[i]:
                show_scheme_card(scheme, token)
    else:
        st.info("Backend not running. Start it with:")
        st.code("uvicorn backend.main:app --reload")
