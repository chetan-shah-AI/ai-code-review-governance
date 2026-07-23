from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = "local"

    github_token: str = ""
    github_webhook_secret: str = ""

    openai_api_key: str
    openai_model: str = "gpt-4.1-mini"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()