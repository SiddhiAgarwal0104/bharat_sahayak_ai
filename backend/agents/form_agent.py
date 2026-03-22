import json
import os

FORM_PATH = "data/forms"

class FormAgent:

    def start_session(self, user_id: int, scheme_id: str):
        return {
            "session_id": f"{user_id}_{scheme_id}"
        }

    def get_step(self, session_id: str, step_n: int, language: str):

        scheme_id = session_id.split("_")[1]
        file_path = os.path.join(FORM_PATH, f"{scheme_id}.json")

        if not os.path.exists(file_path):
            return {"error": "Form not found"}

        with open(file_path, "r") as f:
            data = json.load(f)

        fields = data.get("fields", [])

        if step_n >= len(fields):
            return {"message": "Form completed"}

        field = fields[step_n]

        instruction = field.get(
            "instruction_hi" if language == "hi" else "instruction_en",
            ""
        )

        return {
            "field_name": field.get("field_name"),
            "instruction": instruction,
            "current_index": step_n,
            "total_fields": len(fields)
        }