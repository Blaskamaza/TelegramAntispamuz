from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    BOT_TOKEN: str
    DATABASE_URL: str  # postgresql+asyncpg://user:pass@host/db
    WEBHOOK_URL: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()