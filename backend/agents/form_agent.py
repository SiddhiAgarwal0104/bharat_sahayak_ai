from backend.models.form_field import FormField
from backend.models.user import User, UserSession

class FormAgent:

    async def start_session(self, user_id: str, scheme_id: str) -> str:
        session = UserSession(
            user_id             = user_id,
            scheme_id           = scheme_id,
            current_field_index = 0,
            completed           = False,
        )
        await session.insert()
        return str(session.id)

    async def get_step(self, session_id: str, step_n: int, user_language: str) -> dict:
        session = await UserSession.get(session_id)
        if not session:
            return None

        field = await FormField.find_one(
            FormField.scheme_id == session.scheme_id,
            FormField.field_id  == step_n
        )
        if not field:
            return None

        total = await FormField.find(
            FormField.scheme_id == session.scheme_id
        ).count()

        instruction = field.instruction_hi if user_language == "hi" else field.instruction_en

        prefilled_value = None
        if field.can_prefill and field.prefill_source:
            user = await User.get(session.user_id)
            if user:
                attr = field.prefill_source.split(".")[-1]
                val  = getattr(user, attr, None)
                if val is not None:
                    prefilled_value = str(val)

        return {
            "field_name"     : field.field_name,
            "field_type"     : field.field_type,
            "instruction"    : instruction,
            "prefilled_value": prefilled_value,
            "is_required"    : field.required,
            "document_needed": field.document_needed,
            "validation"     : field.validation,
            "current_index"  : step_n,
            "total_fields"   : total,
        }

    async def advance(self, session_id: str) -> int:
        session = await UserSession.get(session_id)
        session.current_field_index += 1
        await session.save()
        return session.current_field_index

    async def go_back(self, session_id: str) -> int:
        session = await UserSession.get(session_id)
        session.current_field_index = max(0, session.current_field_index - 1)
        await session.save()
        return session.current_field_index

    async def complete_session(self, session_id: str):
        session = await UserSession.get(session_id)
        if session:
            session.completed = True
            await session.save()
