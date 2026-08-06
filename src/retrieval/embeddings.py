from __future__ import annotations

from langchain_openai import OpenAIEmbeddings

from core.config import Settings


def get_embeddings_model(settings: Settings) -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        model=settings.embedding_model,
        api_key=settings.openai_api_key,
    )
