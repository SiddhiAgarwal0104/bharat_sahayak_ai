# backend/utils/eligibility_rules.py

def is_eligible(user: dict, scheme_eligibility: dict) -> bool:
    """
    Returns True if user meets ALL conditions in scheme_eligibility.
    If a key is missing from eligibility dict = no restriction = pass.

    user dict keys:
        age, gender, caste, annual_income, pwd_status, location

    scheme_eligibility keys (all optional):
        min_age, max_age, gender, max_income,
        caste (list), pwd_only, state
    """

    # ── Age ──────────────────────────────────────────────────────
    if scheme_eligibility.get("min_age") is not None:
        if user.get("age", 0) < scheme_eligibility["min_age"]:
            return False

    if scheme_eligibility.get("max_age") is not None:
        if user.get("age", 999) > scheme_eligibility["max_age"]:
            return False

    # ── Gender ───────────────────────────────────────────────────
    if scheme_eligibility.get("gender") is not None:
        if user.get("gender","").upper() != scheme_eligibility["gender"].upper():
            return False

    # ── Income ───────────────────────────────────────────────────
    if scheme_eligibility.get("max_income") is not None:
        if user.get("annual_income", 0) > scheme_eligibility["max_income"]:
            return False

    # ── Caste ────────────────────────────────────────────────────
    if scheme_eligibility.get("caste") is not None:
        allowed = [c.upper() for c in scheme_eligibility["caste"]]
        if user.get("caste", "").upper() not in allowed:
            return False

    # ── PWD ──────────────────────────────────────────────────────
    if scheme_eligibility.get("pwd_only") is True:
        if not user.get("pwd_status", False):
            return False

    # ── State ────────────────────────────────────────────────────
    if scheme_eligibility.get("state") is not None:
        if user.get("location","").lower() != scheme_eligibility["state"].lower():
            return False

    return True