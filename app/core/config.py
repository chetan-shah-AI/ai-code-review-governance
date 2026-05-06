from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_env: str = "local"
    github_token: str
    github_webhook_secret: str

    class Config:
        env_file = ".env"

settings = Settings()


print(settings.github_token)