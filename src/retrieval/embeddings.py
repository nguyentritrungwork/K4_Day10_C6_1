from __future__ import annotations

from langchain_core.embeddings import Embeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_ollama import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings

from core.config import Settings, normalized_provider


def get_embeddings_model(settings: Settings) -> Embeddings:
    provider = normalized_provider(settings)

    if provider == "gemini":
        model = (
            settings.embedding_model
            if "embedding" in settings.embedding_model and "openai" not in settings.embedding_model and "text-embedding-3" not in settings.embedding_model
            else "models/text-embedding-004"
        )
        return GoogleGenerativeAIEmbeddings(
            model=model,
            google_api_key=settings.google_api_key,
        )
    if provider == "openai":
        return OpenAIEmbeddings(
            model=settings.embedding_model,
            api_key=settings.openai_api_key,
        )
    if provider == "openrouter":
        return OpenAIEmbeddings(
            model=settings.embedding_model,
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
        )
    if provider == "ollama":
        return OllamaEmbeddings(
            model=settings.embedding_model or "nomic-embed-text",
            base_url=settings.ollama_base_url,
        )
    if provider == "custom":
        return OpenAIEmbeddings(
            model=settings.embedding_model,
            api_key=settings.custom_llm_api_key or "unused",
            base_url=settings.custom_llm_base_url,
        )

    # Fallback to OpenAIEmbeddings
    return OpenAIEmbeddings(
        model=settings.embedding_model,
        api_key=settings.openai_api_key,
    )
