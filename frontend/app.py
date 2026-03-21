"""
app.py
------
Streamlit main app entry point.
Member 4 owns the full version.
This is Member 3's standalone version to run and test the search page.

Run:
    streamlit run frontend/app.py
"""

import streamlit as st

st.set_page_config(
    page_title="SahayakAI",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar navigation ────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🇮🇳 SahayakAI")
    st.caption("Government Scheme Assistant")
    st.divider()

    if st.session_state.get("token"):
        st.success(f"Logged in")
        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()
    else:
        st.warning("Not logged in")

    st.divider()
    st.caption("Navigation")
    if st.button("Home / Search", use_container_width=True):
        st.switch_page("pages/3_search.py")

# ── Main area: quick login for testing ───────────────────────────────────────
st.title("SahayakAI")
st.write("Government Scheme Assistant — helping citizens find and apply for schemes.")

if not st.session_state.get("token"):
    st.info("For testing Member 3's search features, use the quick login below.")

    with st.form("quick_login"):
        st.subheader("Quick Test Login")
        st.caption("(Full login page built by Member 1)")
        fake_token = st.text_input(
            "Paste a JWT token, or type 'test' to use a demo token",
            value="test"
        )
        submitted = st.form_submit_button("Login")
        if submitted:
            if fake_token == "test":
                # Demo token — works because auth is optional in scheme_router
                st.session_state["token"] = "demo_token_member3_testing"
                st.success("Logged in with demo token.")
                st.rerun()
            else:
                st.session_state["token"] = fake_token
                st.success("Token saved.")
                st.rerun()
else:
    st.success("You are logged in. Use the sidebar or go to the Search page.")
    if st.button("Go to Search →", type="primary"):
        st.switch_page("pages/3_search.py")
