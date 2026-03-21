import os
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/sahayak")

# Cloudinary
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "")
CLOUDINARY_API_KEY    = os.getenv("CLOUDINARY_API_KEY", "")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET", "")

# JWT (used by auth — Member 1 owns this, but needed for get_current_user import)
JWT_SECRET    = os.getenv("JWT_SECRET", "changeme_secret_key")
JWT_ALGORITHM = "HS256"

# App
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
