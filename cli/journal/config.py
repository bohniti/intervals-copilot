from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    backend_url: str = "http://localhost:8000"
    nvidia_api_key: str = ""
    nvidia_model: str = "moonshotai/kimi-k2.5"
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"


def get_settings() -> Settings:
    return Settings()
