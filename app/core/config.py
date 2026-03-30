from pydantic import ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Workforce SaaS"
    VERSION: str = "0.1.0"
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/ai_workforce"
    REDIS_URL: str = "redis://redis:6379"
    GROQ_API_KEY: str = ""

    model_config = ConfigDict(env_file=".env")

settings = Settings()
