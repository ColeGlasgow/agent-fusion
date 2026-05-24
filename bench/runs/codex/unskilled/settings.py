import os


class Settings:
    def __init__(self):
        self.app_name = os.getenv("APP_NAME", "Task Service")


settings = Settings()
