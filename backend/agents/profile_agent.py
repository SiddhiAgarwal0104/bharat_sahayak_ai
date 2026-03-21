# backend/agents/profile_agent.py

import httpx
from bson import ObjectId
from backend.db.database import users_col
from backend.utils.eligibility_rules import is_eligible


class ProfileAgent:

    def get_eligible_scheme_ids(
        self,
        user_id: str,
        intent: str
    ) -> list[str]:
        """
        Returns list of scheme_ids the user is eligible for.

        Steps:
          1. Load user from MongoDB
          2. Fetch all schemes for the intent from Member 3's endpoint
          3. Run eligibility rule engine on each scheme
          4. Return only passing scheme_ids
        """

        # Step 1 — Load user from MongoDB
        user_doc = users_col.find_one({"_id": ObjectId(user_id)})
        if not user_doc:
            return []

        user_dict = {
            "age"          : user_doc.get("age"),
            "gender"       : user_doc.get("gender"),
            "caste"        : user_doc.get("caste"),
            "annual_income": user_doc.get("annual_income"),
            "pwd_status"   : user_doc.get("pwd_status", False),
            "location"     : user_doc.get("location"),
        }

        # Step 2 — Get schemes for this intent from Member 3
        # Until Member 3 is ready, this returns mock data for testing
        try:
            response = httpx.get(
                f"http://localhost:8000/schemes/by-category/{intent}",
                timeout=5.0
            )
            if response.status_code != 200:
                return []
            schemes = response.json()
        except Exception:
            # Member 3 not ready yet — use empty list
            print(f"Warning: scheme service not reachable for intent={intent}")
            return []

        # Step 3 — Filter by eligibility
        eligible_ids = []
        for scheme in schemes:
            criteria = scheme.get("eligibility_criteria", {})
            if is_eligible(user_dict, criteria):
                eligible_ids.append(str(scheme["id"]))

        return eligible_ids