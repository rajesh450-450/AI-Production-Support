from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):

    # =====================================================
    # APPLICATION
    # =====================================================

    app_name: str = "AI Production Support"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"


    # =====================================================
    # GOOGLE GEMINI
    # =====================================================

    google_api_key: str

    model_name: str = "gemini-3.1-flash-lite"

    embedding_model: str = "gemini-embedding-001"

    embedding_dimension: int = 3072


    # =====================================================
    # FAISS / KNOWLEDGE INDEX
    # =====================================================

    faiss_storage_path: str = "data/faiss"

    knowledge_faiss_index_path: str = "data/knowledge.faiss"

    knowledge_faiss_mapping_path: str = "data/faiss_chunk_ids.json"


    # =====================================================
    # ATLASSIAN
    # =====================================================

    atlassian_url: str

    atlassian_email: str

    atlassian_api_token: str

    confluence_space_key: str

    jira_project_key: str


    # =====================================================
    # DATABASE
    # =====================================================

    sqlite_db_path: str = "data/knowledge.db"


    # =====================================================
    # SERVER
    # =====================================================

    host: str = "0.0.0.0"

    port: int = 8000


    # =====================================================
    # PYDANTIC SETTINGS
    # =====================================================

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()