from beanie import PydanticObjectId
from backend.models.user import User
from backend.db.database import get_schemes_collection
from backend.utils.eligibility_rules import is_eligible
import asyncio

class ProfileAgent:

    async def get_eligible_scheme_ids(self, user_id: str, intent: str) -> list:
        print(f"[ProfileAgent] START user={user_id} intent={intent}", flush=True)

        # Load user via Beanie (async — do it here, not in thread)
        user = await User.get(PydanticObjectId(user_id))
        if not user:
            print("[ProfileAgent] User not found!", flush=True)
            return []

        user_dict = {
            "age":           user.age,
            "gender":        user.gender,
            "caste":         user.caste,
            "annual_income": user.annual_income,
            "pwd_status":    user.pwd_status,
            "location":      user.location,
        }
        print(f"[ProfileAgent] User loaded: age={user_dict['age']} gender={user_dict['gender']}", flush=True)

        # Run sync MongoDB/eligibility logic in thread
        result = await asyncio.to_thread(self._filter_eligible, user_dict, intent)
        print(f"[ProfileAgent] DONE eligible={len(result)}", flush=True)
        return result

    def _filter_eligible(self, user_dict: dict, intent: str) -> list:
        col = get_schemes_collection()
        query = {"category": intent} if intent and intent != "all" else {}
        schemes_raw = list(col.find(
            query,
            {"_id": 1, "embedding_id": 1, "eligibility_criteria": 1}
        ))
        print(f"[ProfileAgent] Found {len(schemes_raw)} schemes in DB", flush=True)

        eligible_ids = []
        for scheme in schemes_raw:
            criteria = scheme.get("eligibility_criteria") or {}
            if is_eligible(user_dict, criteria):
                embedding_id = scheme.get("embedding_id")
                if embedding_id is not None:
                    eligible_ids.append(embedding_id)

        print(f"[ProfileAgent] eligible={len(eligible_ids)}/{len(schemes_raw)}", flush=True)
        return eligible_ids