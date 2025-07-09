import re
import json
import psycopg2
from typing import List
from sentence_transformers import SentenceTransformer
from harvester import (
    _harvest_datahub,
    _harvest_fsgeodata,
    _harvest_rda,
    merge_docs,
    find_duplicate_documents,
)


pg_connection_string = "dbname=postgres user=postgres password=sql77! host='0.0.0.0'"

def retrieve_docs():
    """Retrieve documents from various sources."""
    docs = []

    fsgeodata_docs = _harvest_fsgeodata()
    datahub_docs = _harvest_datahub()
    rda_docs = _harvest_rda()

    docs = merge_docs(fsgeodata_docs, datahub_docs, rda_docs)

    duplicates = find_duplicate_documents(docs)
    if duplicates:
        print(f"Found {len(duplicates)} duplicate documents based on title:")
        for dup in duplicates:
            print(f"- {dup['id']}: {dup['title']}, {dup['keywords']}")

    return docs


def chunk_by_sentences(text: str, max_sentences: int = 3) -> List[str]:
    """Split text into chunks by sentence groups"""
    # Split by sentence-ending punctuation
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) <= max_sentences:
        return [text]
    
    chunks = []
    for i in range(0, len(sentences), max_sentences):
        chunk_sentences = sentences[i:i + max_sentences]
        chunk = '. '.join(chunk_sentences)
        if not chunk.endswith('.'):
            chunk += '.'
        chunks.append(chunk)
    
    return chunks


def empty_documents_table():
    """Empty the documents table in the vector database."""
    
    with psycopg2.connect(pg_connection_string) as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM documents")
        conn.commit()
        cur.close()
    print("Documents table emptied.")


def save_to_vector_db(embedding, metadata, title="", desc=""):
    with psycopg2.connect(pg_connection_string) as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO documents (doc_id, chunk_type, chunk_index, chunk_text, embedding, title, description) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (metadata['doc_id'], metadata['chunk_type'], metadata['chunk_index'], metadata['chunk_text'], embedding.tolist(), title, desc)
            )
        except psycopg2.errors.UniqueViolation as e: # psycopg2.errors.UniqueViolation:            
            print(f"IntegrityError: {e}, doc_id: {metadata['doc_id']}")
            conn.rollback()
        conn.commit()
        cur.close()


def load_usfs_docs_into_postgres():

    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    json_data = None
    with open("./tmp/usfs_docs.json", "r") as f:
        json_data = json.load(f)

    doc_count = 0
    for doc in json_data:
        title = doc.get("title", "")
        desc = doc.get("description", "")
        combined_text = f"{title}. {desc}" if title and desc else title or desc

        # Optionally chunk the combined text if it's long
        combined_chunks = chunk_by_sentences(combined_text, max_sentences=5)
        for idx, chunk in enumerate(combined_chunks):
            metadata = {
                'doc_id': doc.get('id'),
                'chunk_type': 'title+description',
                'chunk_index': idx,  # Assuming we are saving the first chunk for simplicity
                'chunk_text': chunk,
                'title': title,
                'description': desc,
            }
            save_to_vector_db(embedding=model.encode(chunk), metadata=metadata, title=title, desc=desc)        

        doc_count += 1
        if doc_count > 10:      
            break

def main():
    # docs = retrieve_docs()
    # print(f"Total documents extracted: {len(docs)}")

    # with open("./tmp/usfs_docs.json", "w") as f:
    #     json.dump(docs, f, indent=2, ensure_ascii=False)

    empty_documents_table()
    load_usfs_docs_into_postgres()


if __name__ == "__main__":
    main()
