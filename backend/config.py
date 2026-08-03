from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "Smart Competency Diagnostic API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = "supersecretkey" # Change in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    DATABASE_URL: str = "sqlite+aiosqlite:///./scd.db"
    FRONTEND_URL: str = "http://localhost:3000"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL: str = "anthropic/claude-3-haiku"
    OPENROUTER_FREE_LIMIT: int = 100
    GOOGLE_AI_API_KEY: str = ""
    GOOGLE_AI_MODEL: str = "gemini-1.5-flash"
    
    ENABLE_FALLBACK: bool = True
    AI_TIMEOUT_SECONDS: int = 30
    AI_MAX_RETRIES: int = 3
    
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE_MB: int = 5
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "docx", "txt"]
    
    MODEL_PATH: str = "models/model.pkl"
    MODEL_VERSION: str = "v1"
    HYBRID_ALPHA: float = 0.5
    
    TESSERACT_CMD: str = "tesseract"
    OCR_CONFIDENCE_THRESHOLD: float = 60.0
    
    SHORTLIST_THRESHOLD: float = 75.0
    REVIEW_THRESHOLD: float = 60.0
    
    FAIRNESS_DIR_THRESHOLD: float = 0.8
    FAIRNESS_DP_THRESHOLD: float = 0.1
    FAIRNESS_EO_THRESHOLD: float = 0.1
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
