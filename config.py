import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "adaptivelearn-ai-secret-2026")
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
    PORT = int(os.getenv("PORT", 5000))

    # MySQL Database Config
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "adaptivelearn_db")

    # Resilient Demo Fallback
    USE_SQLITE_FALLBACK = os.getenv("USE_SQLITE_FALLBACK", "True").lower() in ("true", "1", "t")
    SQLITE_PATH = BASE_DIR / "database" / "adaptivelearn.sqlite3"

    # Mastery Gating
    MASTERY_THRESHOLD = float(os.getenv("MASTERY_THRESHOLD", 70.0))

    # AI & YouTube
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
    DEMO_MODE = os.getenv("DEMO_MODE", "True").lower() in ("true", "1", "t") or not os.getenv("GEMINI_API_KEY")

    # Paths
    BASE_DIR = BASE_DIR
    DB_DIR = BASE_DIR / "database"
    SCHEMA_SQL_PATH = DB_DIR / "schema.sql"
    SEED_SQL_PATH = DB_DIR / "seed.sql"
    ML_MODEL_PATH = BASE_DIR / "ml" / "trained_model.joblib"
