import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"

import asyncio
import traceback
from datetime import datetime
from backend.agents.input_agent import InputAgent
from backend.agents.profile_agent import ProfileAgent
from backend.agents.search_agent import SearchAgent
from backend.agents.explainer_agent import ExplainerAgent
from backend.agents.form_agent import FormAgent

input_agent     = InputAgent()
profile_agent   = ProfileAgent()
search_agent    = SearchAgent()
explainer_agent = ExplainerAgent()
form_agent      = FormAgent()


class Orchestrator:
    async def handle(self, request: dict) -> dict:
        user_id  = request.get("user_id")
        action   = request.get("action", "query")
        language = request.get("language", "hi")
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"[Orchestrator] {ts} user={user_id} action={action}", flush=True)

        if action == "query":
            try:
                input_data = {
                    "type"   : request.get("input_type", "text"),
                    "content": request.get("content", ""),
                }
                intent_obj = input_agent.process(input_data)
                print(f"[Orchestrator] ✅ intent={intent_obj.get('intent')}", flush=True)

                eligible_ids = await profile_agent.get_eligible_scheme_ids(
                    user_id, intent_obj.get("intent", "")
                )
                print(f"[Orchestrator] ✅ eligible={len(eligible_ids)}", flush=True)

                top_3 = search_agent.search(intent_obj, eligible_ids)
                print(f"[Orchestrator] ✅ top_3={len(top_3)}", flush=True)

                return {
                    "action" : "query",
                    "schemes": top_3,
                    "intent" : intent_obj.get("intent", ""),
                }

            except Exception as e:
                print(f"[Orchestrator] ❌ ERROR in query: {e}", flush=True)
                traceback.print_exc()
                return {
                    "action" : "query",
                    "schemes": [],
                    "intent" : "",
                    "error"  : str(e),
                }

        elif action == "explain":
            try:
                scheme = request.get("scheme", {})
                text   = await asyncio.to_thread(
                    explainer_agent.explain, scheme, language
                )
                return {"action": "explain", "text": text}

            except Exception as e:
                print(f"[Orchestrator] ❌ ERROR in explain: {e}", flush=True)
                traceback.print_exc()
                return {"action": "explain", "text": "", "error": str(e)}

        elif action == "apply":
            try:
                scheme_id  = request.get("scheme_id")
                session_id = await form_agent.start_session(user_id, scheme_id)
                first_step = await form_agent.get_step(session_id, 0, language)
                return {
                    "action"    : "apply",
                    "session_id": session_id,
                    "first_step": first_step,
                }

            except Exception as e:
                print(f"[Orchestrator] ❌ ERROR in apply: {e}", flush=True)
                traceback.print_exc()
                return {"action": "apply", "error": str(e)}

        else:
            return {"error": f"Unknown action: {action}"}