"""
scheme_card.py
--------------
Reusable Streamlit component that renders a single scheme card.
Member 3 owns this file.

Usage:
    from frontend.components.scheme_card import show_scheme_card
    show_scheme_card(scheme_dict, token="Bearer ...")
"""

import streamlit as st

# Category colours for badges
CATEGORY_COLORS = {
    "health":      {"bg": "#E6F1FB", "text": "#0C447C", "label": "Health"},
    "pension":     {"bg": "#FAEEDA", "text": "#B06000", "label": "Pension"},
    "agriculture": {"bg": "#EAF3DE", "text": "#3B6D11", "label": "Agriculture"},
    "women":       {"bg": "#FBEAF0", "text": "#99355A", "label": "Women"},
}


def show_scheme_card(scheme: dict, token: str = ""):
    """
    Render a scheme card inside a Streamlit container.

    Args:
        scheme: dict with keys: id, name, category, description,
                benefits, docs_needed, form_url, guidelines_pdf_url,
                match_score, is_best_match
        token:  JWT token string (passed to Apply/Explain navigations)
    """
    cat      = scheme.get("category", "health").lower()
    cat_info = CATEGORY_COLORS.get(cat, CATEGORY_COLORS["health"])

    with st.container(border=True):

        # ── Header row: name + best match badge ──────────────────────────────
        col_name, col_badge = st.columns([5, 1])

        with col_name:
            st.markdown(f"**{scheme.get('name', 'Unknown Scheme')}**")

        with col_badge:
            if scheme.get("is_best_match"):
                st.markdown(
                    "<div style='background:#1A7A5E;color:white;padding:3px 8px;"
                    "border-radius:10px;font-size:11px;text-align:center'>"
                    "&#11088; Best</div>",
                    unsafe_allow_html=True,
                )

        # ── Category badge ────────────────────────────────────────────────────
        st.markdown(
            f"<span style='background:{cat_info['bg']};color:{cat_info['text']};"
            f"padding:2px 10px;border-radius:10px;font-size:11px;"
            f"font-weight:600'>{cat_info['label']}</span>",
            unsafe_allow_html=True,
        )
        st.write("")  # small spacer

        # ── Description snippet ───────────────────────────────────────────────
        desc = scheme.get("description", "")
        st.caption(desc[:220] + "..." if len(desc) > 220 else desc)

        # ── Benefits highlight ────────────────────────────────────────────────
        benefits = scheme.get("benefits", "")
        if benefits:
            st.success(benefits[:180] + "..." if len(benefits) > 180 else benefits)

        # ── Match score ───────────────────────────────────────────────────────
        score = scheme.get("match_score")
        if score and score > 0:
            pct = min(int(score * 100), 100)
            st.progress(pct, text=f"Match: {pct}%")

        # ── Action buttons ────────────────────────────────────────────────────
        btn1, btn2, btn3 = st.columns(3)

        with btn1:
            if st.button("Explain", key=f"explain_{scheme['id']}", use_container_width=True):
                st.session_state["explain_scheme_id"] = scheme["id"]
                st.session_state["explain_scheme"]    = scheme
                st.switch_page("pages/4_scheme_detail.py")

        with btn2:
            if st.button("Apply", key=f"apply_{scheme['id']}", use_container_width=True):
                st.session_state["apply_scheme_id"] = scheme["id"]
                st.session_state["apply_scheme"]    = scheme
                st.switch_page("pages/5_form_guide.py")

        with btn3:
            pdf_url  = scheme.get("guidelines_pdf_url") or ""
            form_url = scheme.get("form_url") or ""
            if pdf_url.startswith("http"):
                st.link_button("View PDF", pdf_url, use_container_width=True)
            elif form_url.startswith("http"):
                st.link_button("Official Site", form_url, use_container_width=True)
            else:
                st.link_button("View PDF", "https://www.india.gov.in", use_container_width=True)