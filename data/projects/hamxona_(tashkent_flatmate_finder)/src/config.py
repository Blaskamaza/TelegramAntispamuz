from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Hamxona MVP"
    DATABASE_URL: str
    BOT_TOKEN: str  # From BotFather

    class Config:
        env_file = ".env"

settings = Settings()