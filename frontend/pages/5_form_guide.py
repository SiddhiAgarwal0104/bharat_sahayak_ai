import streamlit as st
import requests

BACKEND = "http://localhost:8000"

token      = st.session_state.get("token", "")
headers    = {"Authorization": f"Bearer {token}"}
apply_scheme = st.session_state.get("apply_scheme") or {}
scheme_id    = st.session_state.get("apply_scheme_id") or str(apply_scheme.get("id", ""))
scheme_url   = st.session_state.get("apply_scheme_url") or apply_scheme.get("form_url", "")
if not scheme_id:
    st.error("No scheme selected. Go back and click Apply Now.")
    if st.button("Back to Search"):
        st.switch_page("pages/3_search.py")
    st.stop()

st.title("Form Filling Guide")
st.caption("Follow each step below while filling the form on the government website.")
st.markdown("---")

if not st.session_state.get("form_session_id"):
    with st.spinner("Starting form guidance..."):
        try:
            resp = requests.post(
                f"{BACKEND}/form/{scheme_id}/start",
                headers=headers, timeout=15
            )
            if resp.ok:
                data = resp.json()
                st.session_state["form_session_id"] = data["session_id"]
                st.session_state["form_step"]       = data["first_step"]
            else:
                st.error(f"Could not start session: {resp.status_code} {resp.text}")
                st.stop()
        except Exception as e:
            st.error(f"Backend connection error: {e}")
            st.stop()

session_id = st.session_state["form_session_id"]
step       = st.session_state.get("form_step")

left_col, right_col = st.columns([1, 1])

with left_col:
    st.subheader("Step-by-Step Instructions")
    import sys, os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    from frontend.components.form_stepper import render_stepper
    action = render_stepper(step)

    if action == "next":
        with st.spinner("Loading next field..."):
            try:
                resp = requests.post(
                    f"{BACKEND}/form/{scheme_id}/next",
                    params={"session_id": session_id},
                    headers=headers, timeout=15
                )
                if resp.ok:
                    new_step = resp.json()
                    if new_step and not new_step.get("completed"):
                        st.session_state["form_step"] = new_step
                    else:
                        requests.post(
                            f"{BACKEND}/form/{scheme_id}/complete",
                            params={"session_id": session_id},
                            headers=headers
                        )
                        st.session_state["form_step"] = None
                    st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    elif action == "back":
        with st.spinner("Going back..."):
            try:
                resp = requests.post(
                    f"{BACKEND}/form/{scheme_id}/back",
                    params={"session_id": session_id},
                    headers=headers, timeout=15
                )
                if resp.ok:
                    st.session_state["form_step"] = resp.json()
                    st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

with right_col:
    st.subheader("Government Website")
    if scheme_url:
        st.info(f"Open this link in a new tab:\n\n[{scheme_url}]({scheme_url})\n\nThis guide follows the exact field order on that page.")
    else:
        st.info("Open the official government website in a new tab.")

    st.subheader("Tips")
    st.markdown("- Keep your Aadhaar card handy\n- Keep your bank passbook open\n- Use the same name as on your Aadhaar\n- Take a screenshot after each completed field\n- Do not close the form tab between steps")

    if step and step.get("total_fields"):
        done  = step["current_index"]
        total = step["total_fields"]
        st.metric("Overall Progress", f"{int(done/total*100)}%", f"{done} of {total} fields guided")
