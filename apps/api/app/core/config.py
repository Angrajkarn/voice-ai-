# Core configuration for AI Voice Calling Platform API


from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_NAME: str = "VoiceAI API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/voiceai"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_MAX_CONNECTIONS: int = 50

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    CELERY_TASK_TRACK_STARTED: bool = True
    CELERY_TASK_TIME_LIMIT: int = 30 * 60  # 30 minutes

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ENCRYPTION_KEY: str = "your-encryption-key-change-in-production"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:3001"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]

    # Twilio
    TWILIO_ACCOUNT_SID: str | None = None
    TWILIO_AUTH_TOKEN: str | None = None
    TWILIO_PHONE_NUMBER: str | None = None
    TWILIO_APPLICATION_SID: str | None = None
    TWILIO_WEBHOOK_BASE_URL: str | None = None

    # OpenAI (for AI agent logic, NOT for TTS - we use free TTS)
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_REALTIME_MODEL: str = "gpt-4o-realtime-preview"

    # Free TTS Configuration
    FREE_TTS_ENGINE: str = "piper"  # piper, coqui, espeak, system
    PIPER_PATH: str = "piper"  # Path to piper binary
    COQUI_MODEL: str = "tts_models/multilingual/multi-dataset/xtts_v2"
    FREE_TTS_CACHE_DIR: str = "./storage/tts_cache"

    # Google
    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None
    GOOGLE_REDIRECT_URI: str | None = None
    GOOGLE_SHEETS_SCOPES: list[str] = ["https://www.googleapis.com/auth/spreadsheets"]
    GOOGLE_DRIVE_SCOPES: list[str] = ["https://www.googleapis.com/auth/drive.file"]

    # n8n
    N8N_WEBHOOK_URL: str | None = None
    N8N_API_KEY: str | None = None

    # File Storage
    STORAGE_TYPE: str = "local"  # local, s3, gcs
    STORAGE_LOCAL_PATH: str = "./storage"
    STORAGE_MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    STORAGE_ALLOWED_TYPES: list[str] = ["audio/mpeg", "audio/wav", "audio/mp3", "text/csv", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]

    # Calling
    DEFAULT_CALLING_WINDOW_START: str = "09:00"
    DEFAULT_CALLING_WINDOW_END: str = "18:00"
    DEFAULT_CALLING_TIMEZONE: str = "Asia/Kolkata"
    DEFAULT_MAX_CALLS_PER_DAY: int = 100
    DEFAULT_DELAY_BETWEEN_CALLS: int = 30
    DEFAULT_MAX_RETRY_ATTEMPTS: int = 3
    DEFAULT_SKIP_WEEKENDS: bool = True
    MAX_CONCURRENT_CALLS: int = 10

    # Callbacks
    DEFAULT_ALLOW_CALLBACKS: bool = True
    DEFAULT_CALLBACK_WINDOW_START: str = "09:00"
    DEFAULT_CALLBACK_WINDOW_END: str = "18:00"
    DEFAULT_MAX_CALLBACK_DAYS: int = 7
    CALLBACK_REMINDER_MINUTES: int = 15

    # Google Sheets Sync
    SHEETS_SYNC_BATCH_SIZE: int = 100
    SHEETS_SYNC_RETRY_ATTEMPTS: int = 3
    SHEETS_SYNC_RETRY_DELAY: int = 60

    # Monitoring
    PROMETHEUS_ENABLED: bool = True
    PROMETHEUS_PORT: int = 9090
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()