from os import getenv

MONGO_URI = getenv("MONGO_URI")
APP_ENV = getenv("APP_ENV")
API_VERSION = "v26.02"

JWT_SECRET = getenv("JWT_SECRET", "dev-secret-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(getenv("JWT_EXPIRE_MINUTES", "1440"))  # 24 horas

# Email
GMAIL_USER = getenv("GMAIL_USER", "")
GMAIL_APP_PASSWORD = getenv("GMAIL_APP_PASSWORD", "")
FRONTEND_URL = getenv("FRONTEND_URL", "http://localhost:5173")