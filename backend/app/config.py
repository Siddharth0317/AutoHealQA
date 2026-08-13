import os
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str = "AutoHealQA Engine"
    API_V1_STR: str = "/api/v1"
    
    # Environment & Server
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("BACKEND_PORT") or "8000")
    ADMIN_PASSCODE: str = os.getenv("ADMIN_PASSCODE", "admin123")
    
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "*"
    ]

    @property
    def cors_origins_list(self) -> List[str]:
        if isinstance(self.CORS_ORIGINS, str):
            cleaned = self.CORS_ORIGINS.strip("[]'\" ")
            return [origin.strip(" '\"") for origin in cleaned.split(",") if origin.strip()]
        return list(self.CORS_ORIGINS)

    # Groq AI Credentials
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

    # Supabase Credentials
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "https://placeholder.supabase.co")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "placeholder_anon_key")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
