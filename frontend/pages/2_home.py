# frontend/pages/2_home.py

import streamlit as st
import requests

BACKEND = "http://localhost:8000"

# ── Auth guard ───────────────────────────────────────────────────
if "token" not in st.session_state or not st.session_state["token"]:
    st.warning("Please register or login first.")
    st.switch_page("pages/1_register.py")
    st.stop()

token   = st.session_state["token"]
headers = {"Authorization": f"Bearer {token}"}
user    = st.session_state.get("user", {})

st.set_page_config(page_title="SahayakAI — Home", layout="wide")

# ── Greeting ─────────────────────────────────────────────────────
st.markdown(f"## 👋 Namaste, {user.get('name', 'User')}!")
st.markdown("Here are government schemes you may be eligible for.")
st.divider()

# ── Profile card ─────────────────────────────────────────────────
with st.expander("📋 Your Profile", expanded=False):
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Age",      user.get("age", "—"))
    c2.metric("Location", user.get("location", "—"))
    c3.metric("Income",   f"₹{user.get('annual_income', 0):,.0f}")
    c4.metric("Language", user.get("language_pref", "hi").upper())

st.divider()

# ── Recommended schemes ──────────────────────────────────────────
st.subheader("🌟 Recommended for You")

with st.spinner("Loading your schemes..."):
    try:
        resp = requests.get(
            f"{BACKEND}/schemes/recommended",
            headers=headers,
            timeout=10
        )
        schemes = resp.json() if resp.status_code == 200 else []
    except Exception:
        schemes = []
        st.warning("Backend not reachable. Start the server first.")

# ── Scheme cards ─────────────────────────────────────────────────
cat_icons = {
    "agriculture": "🌾",
    "health"     : "🏥",
    "education"  : "🎓",
    "pension"    : "👴",
    "women"      : "👩",
}

if schemes:
    cols = st.columns(min(len(schemes), 3))
    for i, scheme in enumerate(schemes[:3]):
        with cols[i]:
            if scheme.get("is_best_match"):
                st.markdown("⭐ **Best Match**")
            with st.container(border=True):
                cat  = scheme.get("category", "general")
                icon = cat_icons.get(cat, "📋")
                st.markdown(f"### {icon} {scheme.get('name','Scheme')}")
                st.markdown(f"`{cat.upper()}`")
                st.markdown(scheme.get("description","")[:120] + "...")

                c1, c2 = st.columns(2)
                with c1:
                    if st.button("📖 Explain", key=f"exp_{i}",
                                 use_container_width=True):
                        st.session_state["selected_scheme"] = scheme
                        st.switch_page("pages/4_scheme_detail.py")
                with c2:
                    if st.button("📝 Apply", key=f"app_{i}",
                                 use_container_width=True):
                        st.session_state["selected_scheme"] = scheme
                        st.switch_page("pages/5_form_guide.py")
else:
    st.info("No recommendations yet. Use Search to find schemes.")

st.divider()

# ── Bottom actions ────────────────────────────────────────────────
c1, c2 = st.columns(2)
with c1:
    if st.button("🔍 Search Schemes",
                 use_container_width=True, type="primary"):
        st.switch_page("pages/3_search.py")
with c2:
    st.markdown("**📂 My Form Progress**")
    st.caption("No forms in progress yet.")

