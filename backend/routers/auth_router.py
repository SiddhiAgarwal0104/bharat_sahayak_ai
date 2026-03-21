# backend/routers/auth_router.py
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field

from backend.config import settings
from backend.models.user import User

router        = APIRouter(prefix="/auth", tags=["auth"])
pwd_context   = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ── Schemas ────────────────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    name:          str
    age:           int
    location:      str
    area:          str
    caste:         str
    annual_income: float
    gender:        str
    pwd_status:    bool = False
    language_pref: str  = "hi"
    email:         EmailStr
    password:      str = Field(min_length=8, max_length=72)

class LoginRequest(BaseModel):
    email:    EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    user_id:      str
    name:         str


# ── Helpers ────────────────────────────────────────────────────────────────────
def _hash(pw: str) -> str:
    return pwd_context.hash(pw)

def _verify(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def _make_token(data: dict) -> str:
    p = data.copy()
    p["exp"] = datetime.utcnow() + timedelta(minutes=60 * 24 * 7)
    return jwt.encode(p, settings.JWT_SECRET, algorithm="HS256")


# ── Dependency ─────────────────────────────────────────────────────────────────
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    err = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        uid: str = payload.get("user_id")
        if not uid:
            raise err
    except JWTError:
        raise err
    user = await User.get(uid)
    if not user:
        raise err
    return user


# ── POST /auth/register ────────────────────────────────────────────────────────
@router.post("/register", status_code=201)
async def register(p: RegisterRequest):
    existing = await User.find_one(User.email == p.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        hashed_password = _hash(p.password)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Password must be between 8 and 72 characters.",
        )

    user = User(
        name           = p.name,
        age            = p.age,
        location       = p.location,
        area           = p.area,
        caste          = p.caste,
        annual_income  = p.annual_income,
        gender         = p.gender,
        pwd_status     = p.pwd_status,
        language_pref  = p.language_pref,
        email          = p.email,
        hashed_password= hashed_password,
    )
    await user.insert()
    return {"success": True, "user_id": str(user.id)}


# ── POST /auth/login ───────────────────────────────────────────────────────────
@router.post("/login", response_model=TokenResponse)
async def login(p: LoginRequest):
    user = await User.find_one(User.email == p.email)
    if not user or not _verify(p.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    token = _make_token({"user_id": str(user.id), "email": user.email})
    return TokenResponse(access_token=token, user_id=str(user.id), name=user.name)


# ── GET /auth/me ───────────────────────────────────────────────────────────────
@router.get("/me")
async def me(current_user: User = Depends(get_current_user)):
    return {
        "id":            str(current_user.id),
        "name":          current_user.name,
        "email":         current_user.email,
        "age":           current_user.age,
        "caste":         current_user.caste,
        "annual_income": current_user.annual_income,
        "gender":        current_user.gender,
        "pwd_status":    current_user.pwd_status,
        "language_pref": current_user.language_pref,
        "location":      current_user.location,
        "area":          current_user.area,
    }