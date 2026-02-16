from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "postgresql+asyncpg://cyberdemo:cyberdemo@localhost:5433/cyberdemo"

    # External Services
    mock_server_url: str = "http://localhost:5000"
    anthropic_api_key: str = ""

    # OpenSearch
    opensearch_host: str = "localhost"
    opensearch_port: int = 9200

    # App
    debug: bool = True
    app_name: str = "CyberDemo SOC Agent"
    cors_origins: list[str] = [
        "http://localhost:3000", "http://localhost:3001", "http://localhost:3002",
        "http://localhost:3003", "http://localhost:3004", "http://localhost:3005",
        "http://localhost:4000", "http://localhost:5173", "http://localhost:5174"
    ]

    # Agent Config
    auto_contain_confidence_threshold: float = 0.85
    vip_tags: list[str] = ["vip", "executive", "domain-controller", "critical-infra"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
