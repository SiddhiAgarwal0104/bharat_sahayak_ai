# backend/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # These names MUST match exactly what is in your .env file
    MONGO_URL: str
    MONGO_DB: str = "sahayak"
    JWT_SECRET: str
    BACKEND_URL: str = "http://localhost:8000"
    GEMINI_API_KEY: str = ""
    ALLOWED_ORIGINS: str = "http://localhost:8501"
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()