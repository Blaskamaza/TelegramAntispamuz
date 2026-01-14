from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "InglizchaAI"
    TELEGRAM_BOT_TOKEN: str
    OPENAI_API_KEY: str
    SUPABASE_URL: str
    SUPABASE_KEY: str
    WEBHOOK_URL: str  # Public HTTPS url of the server
    ADMIN_IDS: list[int] = []

    class Config:
        env_file = ".env"

settings = Settings()