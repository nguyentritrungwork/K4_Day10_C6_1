from __future__ import annotations

from typing import Any

from core.config import Settings


def get_embeddings_model(settings: Settings) -> Any:
    if "minilm" in settings.embedding_model.lower():
        from langchain_community.embeddings import HuggingFaceEmbeddings
        return HuggingFaceEmbeddings(model_name=settings.embedding_model)
        
    from langchain_openai import OpenAIEmbeddings
    return OpenAIEmbeddings(
        model=settings.embedding_model,
        api_key=settings.openai_api_key,
    )
