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
        print(f"[Orchestrator] {ts} user={user_id} action={action}")

        if action == "query":
            intent_obj = input_agent.process({
                "type"   : request.get("input_type", "text"),
                "content": request.get("content", ""),
            })
            eligible_ids = profile_agent.get_eligible_scheme_ids(
                user_id, intent_obj.get("intent", ""))
            top_3 = search_agent.search(intent_obj, eligible_ids)
            return {
                "action" : "query",
                "schemes": top_3,
                "intent" : intent_obj.get("intent", ""),
            }

        elif action == "explain":
            scheme = request.get("scheme", {})
            text   = explainer_agent.explain(scheme, language)
            return {"action": "explain", "text": text}

        elif action == "apply":
            scheme_id  = request.get("scheme_id")
            session_id = await form_agent.start_session(user_id, scheme_id)
            first_step = await form_agent.get_step(session_id, 0, language)
            return {
                "action"    : "apply",
                "session_id": session_id,
                "first_step": first_step,
            }

        else:
            return {"error": f"Unknown action: {action}"}
