# backend/models/user.py
from datetime import datetime
from beanie import Document
from pydantic import EmailStr

class User(Document):
    name:            str
    age:             int
    location:        str       # state
    area:            str       # district
    caste:           str       # General | OBC | SC | ST
    annual_income:   float
    gender:          str       # M | F | O
    pwd_status:      bool  = False
    language_pref:   str   = "hi"
    email:           EmailStr
    hashed_password: str
    created_at:      datetime = datetime.utcnow()

    class Settings:
        name = "users"
        indexes = ["email"]

class UserSession(Document):
    user_id:             str
    scheme_id:           str
    current_field_index: int  = 0
    started_at:          datetime = datetime.utcnow()
    completed:           bool = False

    class Settings:
        name = "user_sessions"