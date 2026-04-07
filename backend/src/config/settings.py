"""
Application Settings Configuration
Using Pydantic Settings for environment variable management
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # App Configuration
    app_name: str = Field(default="STBank LeadGen API", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")

    # Server Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")

    # Database Configuration
    database_url: str = Field(
        default="postgresql://stbank:password@localhost:5432/stbank_leadgen",
        env="DATABASE_URL",
    )
    database_pool_size: int = Field(default=10, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")

    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    redis_enabled: bool = Field(default=False, env="REDIS_ENABLED")

    # Security Configuration
    secret_key: str = Field(default="change-this-in-production", env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    refresh_token_expire_minutes: int = Field(
        default=10080, env="REFRESH_TOKEN_EXPIRE_MINUTES"  # 7 days
    )

    # CORS Configuration
    cors_origins: list[str] = Field(
        default=["https://lead.stbank.la"], env="CORS_ORIGINS"
    )
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: list[str] = Field(default=["*"], env="CORS_ALLOW_METHODS")
    cors_allow_headers: list[str] = Field(default=["*"], env="CORS_ALLOW_HEADERS")

    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    rate_limit_max_requests: int = Field(default=100, env="RATE_LIMIT_MAX_REQUESTS")
    rate_limit_window_seconds: int = Field(default=60, env="RATE_LIMIT_WINDOW_SECONDS")

    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", env="LOG_FORMAT"
    )

    # Email/SMS Configuration (Optional)
    smtp_host: Optional[str] = Field(default=None, env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_user: Optional[str] = Field(default=None, env="SMTP_USER")
    smtp_password: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    smtp_from: Optional[str] = Field(default=None, env="SMTP_FROM")

    # Core Banking Integration
    core_banking_url: Optional[str] = Field(default=None, env="CORE_BANKING_URL")
    core_banking_api_key: Optional[str] = Field(
        default=None, env="CORE_BANKING_API_KEY"
    )

    # SAML/LDAP Integration
    ldap_enabled: bool = Field(default=False, env="LDAP_ENABLED")
    ldap_server: Optional[str] = Field(default=None, env="LDAP_SERVER")
    ldap_base_dn: Optional[str] = Field(default=None, env="LDAP_BASE_DN")
    ldap_bind_dn: Optional[str] = Field(default=None, env="LDAP_BIND_DN")
    ldap_bind_password: Optional[str] = Field(default=None, env="LDAP_BIND_PASSWORD")
    ldap_use_ssl: bool = Field(default=True, env="LDAP_USE_SSL")

    # WhatsApp/Line Integration
    whatsapp_enabled: bool = Field(default=False, env="WHATSAPP_ENABLED")
    whatsapp_api_url: Optional[str] = Field(default=None, env="WHATSAPP_API_URL")
    whatsapp_token: Optional[str] = Field(default=None, env="WHATSAPP_TOKEN")
    line_enabled: bool = Field(default=False, env="LINE_ENABLED")
    line_channel_id: Optional[str] = Field(default=None, env="LINE_CHANNEL_ID")
    line_channel_secret: Optional[str] = Field(default=None, env="LINE_CHANNEL_SECRET")
    line_access_token: Optional[str] = Field(default=None, env="LINE_ACCESS_TOKEN")

    # Ollama AI Configuration
    ollama_url: str = Field(default="http://localhost:11434", env="OLLAMA_URL")
    ollama_model: str = Field(default="llama3.2", env="OLLAMA_MODEL")
    ollama_enabled: bool = Field(default=False, env="OLLAMA_ENABLED")

    # AI Feature Flags
    ai_scoring_enabled: bool = Field(default=False, env="AI_SCORING_ENABLED")
    ai_chatbot_enabled: bool = Field(default=False, env="AI_CHATBOT_ENABLED")
    ai_analytics_enabled: bool = Field(default=False, env="AI_ANALYTICS_ENABLED")

    # Data Residency (Lao compliance)
    data_residency_country: str = Field(default="Laos", env="DATA_RESIDENCY_COUNTRY")
    audit_retention_years: int = Field(default=7, env="AUDIT_RETENTION_YEARS")

    # Anonymization Settings
    anonymization_retention_days: int = Field(
        default=90, env="ANONYMIZATION_RETENTION_DAYS"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Create settings instance
settings = Settings()
