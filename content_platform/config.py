from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    JWT_PRIVKEY: str
    model_config = SettingsConfigDict(env_file=(".env", ".env.prod"))
