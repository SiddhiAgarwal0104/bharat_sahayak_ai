# tests/test_eligibility.py

from backend.utils.eligibility_rules import is_eligible

# ── Mock users ────────────────────────────────────────────────────
young_obc_woman = {
    "age": 22, "gender": "F", "caste": "OBC",
    "annual_income": 120000, "pwd_status": False,
    "location": "Maharashtra"
}
old_general_man = {
    "age": 65, "gender": "M", "caste": "General",
    "annual_income": 300000, "pwd_status": False,
    "location": "Delhi"
}
pwd_sc_man = {
    "age": 35, "gender": "M", "caste": "SC",
    "annual_income": 80000, "pwd_status": True,
    "location": "UP"
}

# ── Mock scheme eligibility criteria ─────────────────────────────
edu_scheme = {
    "min_age": 18, "max_age": 35, "gender": "F",
    "max_income": 200000, "caste": ["OBC","SC","ST"],
    "pwd_only": False, "state": None
}
pension_scheme = {
    "min_age": 60, "max_age": None, "gender": None,
    "max_income": None, "caste": None,
    "pwd_only": False, "state": None
}
pwd_scheme = {
    "min_age": None, "max_age": None, "gender": None,
    "max_income": 150000, "caste": None,
    "pwd_only": True, "state": None
}
open_scheme = {}   # no restrictions — everyone eligible


# ── Tests ─────────────────────────────────────────────────────────
def test_woman_eligible_for_edu():
    assert is_eligible(young_obc_woman, edu_scheme) == True

def test_old_man_fails_age_for_edu():
    assert is_eligible(old_general_man, edu_scheme) == False

def test_old_man_eligible_for_pension():
    assert is_eligible(old_general_man, pension_scheme) == True

def test_young_fails_pension_age():
    assert is_eligible(young_obc_woman, pension_scheme) == False

def test_pwd_user_eligible():
    assert is_eligible(pwd_sc_man, pwd_scheme) == True

def test_non_pwd_fails_pwd_scheme():
    assert is_eligible(young_obc_woman, pwd_scheme) == False

def test_open_scheme_all_pass():
    assert is_eligible(young_obc_woman, open_scheme) == True
    assert is_eligible(old_general_man, open_scheme) == True
    assert is_eligible(pwd_sc_man,      open_scheme) == True

def test_income_too_high():
    rich = {**young_obc_woman, "annual_income": 500000}
    assert is_eligible(rich, edu_scheme) == False

def test_wrong_gender_fails():
    assert is_eligible(old_general_man, edu_scheme) == False

def test_wrong_caste_fails():
    general_woman = {**young_obc_woman, "caste": "General"}
    assert is_eligible(general_woman, edu_scheme) == False


# ── Run all tests ─────────────────────────────────────────────────
if __name__ == "__main__":
    tests = [
        test_woman_eligible_for_edu,
        test_old_man_fails_age_for_edu,
        test_old_man_eligible_for_pension,
        test_young_fails_pension_age,
        test_pwd_user_eligible,
        test_non_pwd_fails_pwd_scheme,
        test_open_scheme_all_pass,
        test_income_too_high,
        test_wrong_gender_fails,
        test_wrong_caste_fails,
    ]
    passed = 0
    for t in tests:
        try:
            t()
            print(f"  ✅  {t.__name__}")
            passed += 1
        except AssertionError:
            print(f"  ❌  {t.__name__} FAILED")
    print(f"\n{passed}/{len(tests)} tests passed")