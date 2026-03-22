import streamlit as st

def render_stepper(step: dict):
    if not step:
        st.success("All fields complete! Go to the government website to submit.")
        return None

    current     = step.get("current_index", 0)
    total       = step.get("total_fields", 1)
    field_name  = step.get("field_name", "")
    instruction = step.get("instruction", "")
    prefilled   = step.get("prefilled_value")
    doc_needed  = step.get("document_needed")
    validation  = step.get("validation")
    is_required = step.get("is_required", True)

    st.progress((current + 1) / max(total, 1),
                text=f"Field {current + 1} of {total}")

    req = " (required)" if is_required else ""
    st.markdown(f"### {field_name}{req}")
    st.info(instruction)

    if doc_needed:
        st.warning(f"Document needed: {doc_needed}")

    if prefilled:
        st.success(f"Auto-filled from your profile: {prefilled}")
        st.caption("Taken from your registration. Correct if needed.")

    st.text_input(
        label       = "What you will type on the form:",
        value       = str(prefilled) if prefilled else "",
        placeholder = validation or "Enter value here",
        key         = f"field_input_{current}",
    )

    st.markdown("")
    left_col, right_col = st.columns(2)
    action = None

    with left_col:
        if current > 0:
            if st.button("Previous", key=f"back_{current}", use_container_width=True):
                action = "back"

    with right_col:
        label = "Done" if current == total - 1 else "Next"
        if st.button(label, key=f"next_{current}",
                     use_container_width=True, type="primary"):
            action = "next"

    return action
