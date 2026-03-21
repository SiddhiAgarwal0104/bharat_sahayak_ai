"""
3_search.py
-----------
Streamlit search page — Member 3 owns this file.

Features:
- Text input for typing queries
- Voice input (uses Member 1's voice_recorder if available, falls back gracefully)
- Calls NLP service for intent (uses Member 2's endpoint if available)
- Calls scheme search endpoint and displays top-3 cards
"""

import streamlit as st
import requests
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from components.scheme_card import show_scheme_card

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Find Schemes — SahayakAI", layout="wide")

BACKEND = os.getenv("BACKEND_URL", "http://localhost:8000")


# ── Auth check ────────────────────────────────────────────────────────────────
token = st.session_state.get("token", "")
if not token:
    st.warning("Please login first.")
    if st.button("Go to Login"):
        st.switch_page("pages/1_register.py")
    st.stop()

headers = {"Authorization": f"Bearer {token}"}


# ── Page header ───────────────────────────────────────────────────────────────
st.title("Find Government Schemes")
st.caption("Search in English, Hindi, or any Indian language — type or speak your query")
st.divider()


# ── Input row ─────────────────────────────────────────────────────────────────
col_input, col_voice = st.columns([4, 1])

with col_input:
    text_query = st.text_input(
        "Type your query",
        placeholder="e.g. health insurance for family, kisan subsidy, pension for old age",
        label_visibility="collapsed",
    )

with col_voice:
    # Try to import Member 1's voice recorder — fall back gracefully if not ready
    voice_query = ""
    try:
        from components.voice_recorder import voice_recorder
        voice_query = voice_recorder() or ""
    except ImportError:
        if st.button("Voice input\n(not ready yet)"):
            st.info("Voice input will be available once Member 1 completes their module.")


# ── Category quick-filter buttons ────────────────────────────────────────────
st.write("")
st.caption("Or browse by category:")
cat_col1, cat_col2, cat_col3, cat_col4, cat_col5 = st.columns(5)

category_filter = st.session_state.get("category_filter", "")

with cat_col1:
    if st.button("All"):
        st.session_state["category_filter"] = ""
        category_filter = ""
with cat_col2:
    if st.button("Health"):
        st.session_state["category_filter"] = "health"
        category_filter = "health"
with cat_col3:
    if st.button("Pension"):
        st.session_state["category_filter"] = "pension"
        category_filter = "pension"
with cat_col4:
    if st.button("Agriculture"):
        st.session_state["category_filter"] = "agriculture"
        category_filter = "agriculture"
with cat_col5:
    if st.button("Women"):
        st.session_state["category_filter"] = "women"
        category_filter = "women"

st.divider()


# ── Resolve final query ───────────────────────────────────────────────────────
final_query = voice_query or text_query or category_filter


# ── Search ────────────────────────────────────────────────────────────────────
if final_query:

    with st.spinner("Finding best schemes for you..."):

        # Step 1: Get intent classification from NLP service (Member 2)
        # Falls back to category_filter or empty intent if NLP service not ready
        try:
            nlp_resp = requests.post(
                f"{BACKEND}/nlp/classify",
                json={"text": final_query, "language": "auto"},
                headers=headers,
                timeout=5,
            ).json()
            intent     = nlp_resp.get("intent", category_filter or "")
            slots      = nlp_resp.get("slots", {})
            confidence = nlp_resp.get("confidence", 0)
        except Exception:
            # NLP service not ready yet — use category_filter as intent
            intent     = category_filter or ""
            slots      = {}
            confidence = 0
            nlp_resp   = {"query_text": final_query, "language": "en",
                          "intent": intent, "slots": slots}

        # Step 2: Get eligible candidate IDs from profile agent (Member 2)
        # Falls back to empty list → search all schemes
        try:
            profile_resp = requests.get(
                f"{BACKEND}/profile/eligible",
                params={"intent": intent},
                headers=headers,
                timeout=5,
            ).json()
            candidate_ids = profile_resp.get("scheme_ids", [])
        except Exception:
            # Profile agent not ready — pass empty list to search all schemes
            candidate_ids = []

        # Step 3: Search schemes
        try:
            intent_obj = {
                "query_text": final_query,
                "language":   "en",
                "intent":     intent,
                "slots":      slots,
            }
            search_resp = requests.post(
                f"{BACKEND}/schemes/search",
                json={"intent_obj": intent_obj, "candidate_ids": candidate_ids},
                headers=headers,
                timeout=10,
            )
            schemes = search_resp.json()
        except Exception as e:
            st.error(f"Search failed: {e}")
            schemes = []

    # ── Results ───────────────────────────────────────────────────────────────
    if not schemes:
        st.info("No matching schemes found. Try a different query or browse by category.")
    else:
        # Show intent badge
        if intent:
            st.markdown(
                f"Showing results for: "
                f"<span style='background:#EEEDFE;color:#3D2A8A;padding:2px 10px;"
                f"border-radius:10px;font-size:12px;font-weight:600'>"
                f"{intent.upper()}</span>",
                unsafe_allow_html=True,
            )
            st.write("")

        # Render scheme cards in columns
        cols = st.columns(len(schemes))
        for i, scheme in enumerate(schemes):
            with cols[i]:
                show_scheme_card(scheme, token)

# ── Default state: show recommended schemes ───────────────────────────────────
else:
    st.subheader("Recommended for you")
    with st.spinner("Loading recommendations..."):
        try:
            resp = requests.get(
                f"{BACKEND}/schemes/recommended",
                headers=headers,
                timeout=10,
            )
            recommended = resp.json()
        except Exception:
            recommended = []

    if recommended:
        cols = st.columns(min(len(recommended), 3))
        for i, scheme in enumerate(recommended[:3]):
            with cols[i]:
                show_scheme_card(scheme, token)
    else:
        st.info("Could not load recommendations. Make sure the backend is running.")
        st.code("uvicorn backend.main:app --reload")
