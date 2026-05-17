from functools import lru_cache
from typing import Annotated, List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "agente-clasificacion"
    app_env: str = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"

    llm_provider: str = "gemini"
    llm_base_url: str = "https://models.inference.ai.azure.com"
    llm_api_key: str = ""
    llm_model: str = "gpt-4.1-mini"
    gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    llm_timeout: int = 60

    classification_json_path: str = "./anexo_c_clasificacion.json"
    areas_lineas_json_path: str = "./areas_lineas.json"
    lineas_capacidades_json_path: str = "./lineas_capacidades.json"
    top_k_candidates: int = 5
    top_k_areas: int = 3
    final_candidates: int = 2
    min_confidence: float = 0.60
    cors_origins: Annotated[List[str], NoDecode] = Field(default_factory=lambda: ["*"])

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_cors_origins(cls, value: str | List[str]) -> List[str]:
        if isinstance(value, list):
            return value
        if not value:
            return ["*"]
        return [item.strip() for item in value.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
