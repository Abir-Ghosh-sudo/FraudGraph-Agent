from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "FraudGraph Agent"
    app_version: str = "0.1.0"
    environment: Literal["development", "testing", "staging", "production"] = "development"
    debug: bool = False
    api_prefix: str = "/api/v1"
    host: str = "0.0.0.0"
    port: int = Field(default=8000, ge=1, le=65535)

    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
    )

    data_dir: Path = PROJECT_ROOT / "data"
    raw_data_dir: Path = PROJECT_ROOT / "data" / "raw"
    processed_data_dir: Path = PROJECT_ROOT / "data" / "processed"
    benchmark_data_dir: Path = PROJECT_ROOT / "data" / "benchmark"
    documents_dir: Path = PROJECT_ROOT / "data" / "documents"

    dataset_chunk_size: int = Field(default=10_000, ge=100)
    overwrite_processed_data: bool = False

    tigergraph_host: str = ""
    tigergraph_username: str = ""
    tigergraph_password: str = ""
    tigergraph_graph_name: str = ""
    tigergraph_api_token: str = ""
    tigergraph_timeout_seconds: float = Field(default=30.0, gt=0)

    tigergraph_mcp_enabled: bool = False
    tigergraph_mcp_url: str = ""
    tigergraph_mcp_timeout_seconds: float = Field(default=30.0, gt=0)

    tigergraph_investigation_query: str = ""

    tigergraph_gsql_dir: Path = PROJECT_ROOT / "tigergraph"
    tigergraph_schema_dir: Path = PROJECT_ROOT / "tigergraph" / "schema"
    tigergraph_queries_dir: Path = PROJECT_ROOT / "tigergraph" / "queries"
    tigergraph_algorithms_dir: Path = PROJECT_ROOT / "tigergraph" / "algorithms"
    tigergraph_loading_dir: Path = PROJECT_ROOT / "tigergraph" / "loading"

    llm_provider: Literal["ollama"] = "ollama"
    llm_model: str = "llama3.1:8b"
    llm_base_url: str = "http://localhost:11434"
    llm_temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    llm_timeout_seconds: float = Field(default=120.0, gt=0)

    embedding_provider: Literal["sentence_transformers"] = "sentence_transformers"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = Field(default=384, ge=1)

    vector_store: Literal["faiss"] = "faiss"
    vector_store_dir: Path = PROJECT_ROOT / "data" / "processed" / "vector_store"

    graphrag_enabled: bool = True
    graphrag_top_k: int = Field(default=10, ge=1, le=100)
    graphrag_rerank_top_k: int = Field(default=5, ge=1, le=100)
    document_chunk_size: int = Field(default=1000, ge=100)
    document_chunk_overlap: int = Field(default=150, ge=0)

    agent_max_steps: int = Field(default=20, ge=1, le=100)
    agent_timeout_seconds: float = Field(default=300.0, gt=0)
    agent_enable_human_approval: bool = True

    evidence_minimum_score: float = Field(default=0.60, ge=0.0, le=1.0)

    risk_low_threshold: float = Field(default=0.30, ge=0.0, le=1.0)
    risk_medium_threshold: float = Field(default=0.60, ge=0.0, le=1.0)
    risk_high_threshold: float = Field(default=0.85, ge=0.0, le=1.0)
    uncertainty_threshold: float = Field(default=0.40, ge=0.0, le=1.0)

    case_memory_enabled: bool = True
    case_memory_top_k: int = Field(default=5, ge=1, le=50)

    allow_action_execution: bool = False
    require_approval_for_external_actions: bool = True

    sar_enabled: bool = True
    sar_require_policy_check: bool = True

    benchmark_enabled: bool = True
    benchmark_cases_dir: Path = PROJECT_ROOT / "data" / "benchmark" / "cases"
    benchmark_outputs_dir: Path = PROJECT_ROOT / "data" / "benchmark" / "outputs"
    benchmark_max_cases: int = Field(default=20, ge=1)

    outputs_dir: Path = PROJECT_ROOT / "outputs"
    investigations_output_dir: Path = PROJECT_ROOT / "outputs" / "investigations"
    benchmark_output_dir: Path = PROJECT_ROOT / "outputs" / "benchmark"
    reports_output_dir: Path = PROJECT_ROOT / "outputs" / "reports"

    auth_enabled: bool = False
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = Field(default=60, ge=1)

    log_level: str = "INFO"
    log_json: bool = False

    request_timeout_seconds: float = Field(default=30.0, gt=0)
    max_request_body_bytes: int = Field(default=5 * 1024 * 1024, ge=1024)

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def is_testing(self) -> bool:
        return self.environment == "testing"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def tigergraph_configured(self) -> bool:
        has_host = bool(self.tigergraph_host)
        has_graph = bool(self.tigergraph_graph_name)
        has_token = bool(self.tigergraph_api_token)
        has_credentials = bool(
            self.tigergraph_username
            and self.tigergraph_password
        )

        return bool(
            has_host
            and has_graph
            and (has_token or has_credentials)
        )

    @property
    def tigergraph_mcp_configured(self) -> bool:
        return bool(
            self.tigergraph_mcp_enabled
            and self.tigergraph_mcp_url
        )

    @property
    def tigergraph_investigation_configured(self) -> bool:
        return bool(
            self.tigergraph_configured
            and self.tigergraph_investigation_query
        )

    @property
    def llm_configured(self) -> bool:
        return bool(
            self.llm_provider == "ollama"
            and self.llm_model
            and self.llm_base_url
        )

    @property
    def embeddings_configured(self) -> bool:
        return bool(
            self.embedding_provider == "sentence_transformers"
            and self.embedding_model
        )

    @property
    def vector_store_configured(self) -> bool:
        return self.vector_store == "faiss"

    def ensure_runtime_directories(self) -> None:
        directories = (
            self.raw_data_dir,
            self.processed_data_dir,
            self.benchmark_data_dir,
            self.benchmark_cases_dir,
            self.benchmark_outputs_dir,
            self.documents_dir,
            self.vector_store_dir,
            self.investigations_output_dir,
            self.benchmark_output_dir,
            self.reports_output_dir,
        )

        for directory in directories:
            directory.mkdir(
                parents=True,
                exist_ok=True,
            )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()