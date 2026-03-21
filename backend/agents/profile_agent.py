# backend/agents/profile_agent.py

from bson import ObjectId
from backend.db.database import get_db, get_schemes_collection
from backend.utils.eligibility_rules import is_eligible


class ProfileAgent:

    def get_eligible_scheme_ids(
        self,
        user_id: str,
        intent: str
    ) -> list[str]:
        """
        Returns list of scheme embedding_ids the user is eligible for.

        Steps:
          1. Load user from MongoDB
          2. Fetch schemes for the intent directly from DB (no HTTP call)
          3. Run eligibility rule engine on each scheme
          4. Return only passing embedding_ids
        """

        # Step 1 — Load user from MongoDB
        user_doc = get_db()["users"].find_one({"_id": ObjectId(user_id)})
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

        # Step 2 — Fetch schemes directly from DB (fast, no HTTP roundtrip)
        col = get_schemes_collection()
        query = {"category": intent} if intent != "all" else {}
        schemes_raw = list(col.find(
            query,
            {"_id": 1, "embedding_id": 1, "eligibility_criteria": 1, "name": 1}
        ))

        # Step 3 — Filter by eligibility rules
        eligible_ids = []
        for scheme in schemes_raw:
            criteria = scheme.get("eligibility_criteria", {})
            if criteria is None:
                criteria = {}
            if is_eligible(user_dict, criteria):
                embedding_id = scheme.get("embedding_id")
                if embedding_id is not None:
                    eligible_ids.append(embedding_id)

        print(f"[profile_agent] intent={intent}, eligible={len(eligible_ids)}/{len(schemes_raw)}")
        return eligible_ids