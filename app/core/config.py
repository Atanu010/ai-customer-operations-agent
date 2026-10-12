from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ai-customer-operations-agent"
    environment: str = "development"
    database_url: str = ""
    log_level: str = "INFO"
    secret_key: str = "dev-secret-key-change-me"
    llm_provider: str = "mock"
    embedding_provider: str = "mock"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    mock_mode: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def uses_real_llm(self) -> bool:
        return self.llm_provider == "openai" and bool(self.openai_api_key)

    @property
    def uses_real_embeddings(self) -> bool:
        return self.embedding_provider == "openai" and bool(self.openai_api_key)


settings = Settings()
