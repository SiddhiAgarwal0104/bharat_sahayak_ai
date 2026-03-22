from beanie import Document
from typing import Optional

class FormField(Document):
    scheme_id       : str
    field_id        : int
    field_name      : str
    field_type      : str
    required        : bool          = True
    can_prefill     : bool          = False
    prefill_source  : Optional[str] = None
    instruction_en  : str
    instruction_hi  : str
    document_needed : Optional[str] = None
    validation      : Optional[str] = None

    class Settings:
        name = "form_fields"
