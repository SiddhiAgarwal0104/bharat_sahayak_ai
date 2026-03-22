from backend.agents.input_agent import InputAgent
from backend.agents.profile_agent import ProfileAgent
from backend.agents.search_agent import SearchAgent
from backend.agents.explainer_agent import ExplainerAgent
from backend.agents.form_agent import FormAgent

input_agent = InputAgent()
profile_agent = ProfileAgent()
search_agent = SearchAgent()
explainer_agent = ExplainerAgent()
form_agent = FormAgent()

class Orchestrator:

    def handle(self, request: dict):

        action = request.get("action", "query")

        if action == "query":
            intent = input_agent.process({
                "type": "text",
                "content": request.get("content", "")
            })

            eligible = profile_agent.get_eligible_scheme_ids(
                request.get("user_id", 1),
                intent.get("intent", "")
            )

            schemes = search_agent.search(intent, eligible)

            return {"schemes": schemes}

        elif action == "explain":
            return {
                "text": explainer_agent.explain(request.get("scheme", {}))
            }

        elif action == "apply":
            session_id = form_agent.start_session(
                request.get("user_id", 1),
                request.get("scheme_id")
            )

            step = form_agent.get_step(session_id, 0, "hi")

            return {
                "session_id": session_id,
                "first_step": step
            }