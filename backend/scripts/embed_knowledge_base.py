"""
Embedding script — Day 3 deliverable (Section 8.3).
Run with: python -m scripts.embed_knowledge_base
Reads all knowledge_base rows from Postgres, embeds them, and writes them
into the local ChromaDB store so rag_retriever.py can query them.

Re-run this any time knowledge_base rows are added/edited via the admin
panel (Section 9) to keep the vector store in sync.
"""
from app.db.session import SessionLocal
from app.models.models import KnowledgeBase
from app.services.rag_retriever import get_chroma_collection, get_embedding_model

db = SessionLocal()
rows = db.query(KnowledgeBase).all()

if not rows:
    print("No knowledge_base rows found — run `python -m scripts.seed_data` first.")
else:
    model = get_embedding_model()
    collection = get_chroma_collection()

    ids, documents, embeddings, metadatas = [], [], [], []
    for row in rows:
        text = f"{row.condition_name}: {', '.join(row.associated_symptoms)}"
        ids.append(str(row.id))
        documents.append(text)
        embeddings.append(model.encode(text).tolist())
        metadatas.append(
            {
                "condition_name": row.condition_name,
                "category": row.category,
                "typical_severity": row.typical_severity or "",
                "icd_code": row.icd_code or "",
                "guidance_text_en": row.guidance_text_en,
                "guidance_text_de": row.guidance_text_de or "",
                "source_dataset": row.source_dataset or "",
            }
        )

    # upsert keeps this safe to re-run after admin edits
    collection.upsert(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)
    print(f"Embedded {len(rows)} knowledge_base rows into the vector store.")

db.close()
