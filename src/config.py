"""Configuration management for the Instagram Coach Agent."""

import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

# Project paths
ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"
CHROMA_DIR = ROOT_DIR / "chroma_db"


class LLMConfig(BaseModel):
    """Configuration for LLM (Featherless AI)."""

    api_key: str = Field(default_factory=lambda: os.getenv("FEATHERLESS_API_KEY", ""))
    model: str = Field(
        default_factory=lambda: os.getenv("LLM_MODEL", "Llama-3.1-8B-Instruct")
    )
    base_url: str = "https://api.featherless.ai/v1"
    temperature: float = Field(
        default_factory=lambda: float(os.getenv("TEMPERATURE", "0.5"))
    )
    max_tokens: int = Field(
        default_factory=lambda: int(os.getenv("MAX_TOKENS", "1000"))
    )
    top_p: float = Field(default_factory=lambda: float(os.getenv("TOP_P", "0.9")))
    frequency_penalty: float = Field(
        default_factory=lambda: float(os.getenv("FREQUENCY_PENALTY", "0.2"))
    )


class EmbeddingConfig(BaseModel):
    """Configuration for embeddings."""

    model_name: str = Field(
        default_factory=lambda: os.getenv(
            "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
        )
    )
    dimension: int = 384  # Dimension for all-MiniLM-L6-v2


class VectorStoreConfig(BaseModel):
    """Configuration for ChromaDB vector store."""

    persist_directory: str = Field(
        default_factory=lambda: os.getenv("CHROMA_PERSIST_DIR", str(CHROMA_DIR))
    )
    collection_name: str = "instagram_posts"


class Config:
    """Global configuration."""

    llm: LLMConfig = LLMConfig()
    embedding: EmbeddingConfig = EmbeddingConfig()
    vector_store: VectorStoreConfig = VectorStoreConfig()

    # Data paths
    posts_data_path: Path = DATA_DIR / "sample_posts.json"
    profile_data_path: Path = DATA_DIR / "influencer_profile.json"


# Global config instance
config = Config()
