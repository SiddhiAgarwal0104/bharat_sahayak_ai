# backend/models/user.py

from beanie import Document
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class User(Document):
    name           : str
    age            : int
    location       : str
    area           : Optional[str] = None
    caste          : str
    annual_income  : float
    gender         : str
    pwd_status     : bool     = False
    language_pref  : str      = "hi"
    email          : str
    hashed_password: str
    created_at     : datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"


class UserSession(Document):
    user_id             : str
    scheme_id           : str
    current_field_index : int      = 0
    started_at          : datetime = Field(default_factory=datetime.utcnow)
    completed           : bool     = False

    class Settings:
        name = "user_sessions"


class UserCreate(BaseModel):
    name          : str
    age           : int
    location      : str
    area          : Optional[str] = None
    caste         : str
    annual_income : float
    gender        : str
    pwd_status    : bool = False
    language_pref : str  = "hi"
    email         : str
    password      : str


class UserLogin(BaseModel):
    email    : str
    password : str


def user_to_dict(user: User) -> dict:
    return {
        "id"           : str(user.id),
        "name"         : user.name,
        "age"          : user.age,
        "location"     : user.location,
        "area"         : user.area,
        "caste"        : user.caste,
        "annual_income": user.annual_income,
        "gender"       : user.gender,
        "pwd_status"   : user.pwd_status,
        "language_pref": user.language_pref,
        "email"        : user.email,
        "created_at"   : str(user.created_at)
    }
