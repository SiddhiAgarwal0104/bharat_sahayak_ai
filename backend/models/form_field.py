from sqlalchemy import Column, Integer, String, Boolean, Text
from backend.db.database import Base

class FormField(Base):
    __tablename__ = 'form_fields'

    id = Column(Integer, primary_key=True, index=True)
    scheme_id = Column(String, index=True)
    field_id = Column(Integer)
    field_name = Column(String)
    field_type = Column(String)
    required = Column(Boolean, default=True)
    can_prefill = Column(Boolean, default=False)
    prefill_source = Column(String)
    instruction_en = Column(Text)
    instruction_hi = Column(Text)
    document_needed = Column(String)
    validation = Column(String)