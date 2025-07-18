import os
import psycopg2
import numpy as np
from typing import List, Dict, Any, Optional

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

# Load environment variables for DB connection
PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = os.getenv("PG_PORT", "5432")
PG_USER = os.getenv("PG_USER", "postgres")
PG_PASSWORD = os.getenv("PG_PASSWORD", "")
PG_DATABASE = os.getenv("PG_DATABASE", "postgres")

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

def get_db_connection():
    return psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        user=PG_USER,
        password=PG_PASSWORD,
        dbname=PG_DATABASE
    )

def get_embedder():
    if SentenceTransformer is None:
        raise ImportError("sentence-transformers is not installed. Please install it.")
    return SentenceTransformer(EMBEDDING_MODEL_NAME)

def embed_query(query: str, embedder=None) -> np.ndarray:
    if embedder is None:
        embedder = get_embedder()
    emb = embedder.encode([query], normalize_embeddings=True)
    return emb[0]

def search_catalog(
    query: str,
    top_k: int = 5,
    extra_where: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Perform a vector search in the documents table.
    Returns a list of dicts with metadata and distance.
    """
    embedder = get_embedder()
    query_emb = embed_query(query, embedder)
    conn = get_db_connection()
    cur = conn.cursor()
    # Prepare SQL for pgvector similarity search
    sql = """
        SELECT id, title, description, keywords, authors, chunk_text, chunk_index, doc_id, chunk_type, data_source,
               embedding <=> %s AS distance
        FROM documents
    """
    if extra_where:
        sql += f" WHERE {extra_where} "
    sql += " ORDER BY embedding <=> %s LIMIT %s;"
    cur.execute(sql, (query_emb.tolist(), query_emb.tolist(), top_k))
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    results = [dict(zip(columns, row)) for row in rows]
    cur.close()
    conn.close()
    return results

def answer_question(
    question: str,
    context_chunks: List[Dict[str, Any]],
    llm=None
) -> str:
    """
    Stub for Q&A: Given a question and context (top chunks), call an LLM to answer.
    """
    # This is a stub. Integrate with OpenAI, local LLM, etc. as needed.
    context = "\n\n".join(chunk["chunk_text"] for chunk in context_chunks if chunk.get("chunk_text"))
    prompt = f"Answer the following question using the provided context.\n\nContext:\n{context}\n\nQuestion: {question}\nAnswer:"
    if llm is not None:
        return llm(prompt)
    return "[Q&A not implemented: integrate with an LLM provider]"
