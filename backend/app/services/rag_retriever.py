"""
RAG Retriever — Section 8.3.
Embeds the knowledge_base once (via scripts/embed_knowledge_base.py) into a
local ChromaDB collection, then at query time embeds the extracted symptoms
and returns the top-N closest matching conditions, filtered by category
(Section 9.2) for better precision.
"""
from functools import lru_cache

import chromadb
from sentence_transformers import SentenceTransformer

from app.core.config import get_settings

settings = get_settings()

COLLECTION_NAME = "knowledge_base"


@lru_cache
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(settings.EMBEDDING_MODEL)


@lru_cache
def get_chroma_collection():
    client = chromadb.PersistentClient(path=settings.VECTOR_STORE_PATH)
    return client.get_or_create_collection(COLLECTION_NAME)


def retrieve_relevant_conditions(
    extracted_symptoms: list[str], category: str | None = None, top_k: int = 5
) -> list[dict]:
    """
    Returns up to top_k knowledge_base rows most relevant to the given
    symptoms, optionally filtered to a single category (Section 9.2).
    Returns an empty list gracefully if the vector store hasn't been
    seeded yet — callers must handle "no grounding available" without
    crashing (Section 7.5 fallback philosophy).
    """
    if not extracted_symptoms:
        return []

    collection = get_chroma_collection()
    if collection.count() == 0:
        return []

    model = get_embedding_model()
    query_text = ", ".join(extracted_symptoms)
    query_embedding = model.encode(query_text).tolist()

    where_filter = {"category": category} if category else None

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where_filter,
    )

    matches = []
    if results and results.get("metadatas"):
        for meta, doc in zip(results["metadatas"][0], results["documents"][0]):
            matches.append({**meta, "matched_text": doc})
    return matches
