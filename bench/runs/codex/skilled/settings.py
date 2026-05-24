from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Task Service"

    model_config = SettingsConfigDict(env_prefix="TASK_SERVICE_")


settings = Settings()
