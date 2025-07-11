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

def remove_unicode(text):
    return text.encode("ascii", "ignore").decode("ascii")

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
                "INSERT INTO documents (doc_id, chunk_type, chunk_index, chunk_text, embedding, title, description, keywords, data_source) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    metadata['doc_id'],
                    metadata['chunk_type'],
                    metadata['chunk_index'],
                    metadata['chunk_text'],
                    embedding.tolist(),
                    title,
                    remove_unicode(desc),
                    metadata['keywords'],
                    metadata['src']
                )
            )
        except psycopg2.errors.UniqueViolation as e:
            print(f"IntegrityError: {e}, doc_id: {metadata['doc_id']}")
            conn.rollback()
        conn.commit()
        cur.close()


def chunk_document(doc, chunk_size=1000, overlap=200):

    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Combine all text fields into a single text for chunking
    full_text = f"Title: {doc['title']}\n\nDescription: {doc['description']}\n\n"

    # Add keywords if present
    if doc.get('keywords'):
       keywords_text = "Keywords: " + ", ".join(doc['keywords'])
       full_text += keywords_text + "\n\n"

    tokens = model.encode(full_text, convert_to_tensor=True)
    chunks = chunk_by_sentences(full_text, max_sentences=10)


def load_usfs_docs_into_postgres():

    model = SentenceTransformer('all-MiniLM-L6-v2')

    json_data = None
    with open("./tmp/usfs_docs.json", "r") as f:
        json_data = json.load(f)

    doc_count = 0
    for doc in json_data:
        title = doc.get("title", "")
        desc = doc.get("description", "")
        keywords = doc.get("keywords", [])
        source = doc.get("src", "")

        full_text = f"Title: {title}\n\nDescription: {desc}"
        if keywords:
            full_text += f"\n\nKeywords: {', '.join(keywords)}"

        chunks = chunk_by_sentences(full_text, max_sentences=5)
        # embeddings = model.encode(chunks, convert_to_tensor=True)
        embeddings = model.encode(chunks)

        chunked_data = list(zip(chunks, embeddings))
        for idx, chunk in enumerate(chunked_data):
            chunk_text, embedding = chunk
            metadata = {
                'doc_id': doc.get('id'),
                'chunk_type': 'title+description+keywords',
                'chunk_index': idx,
                'chunk_text': chunk_text,
                'title': title,
                'description': desc,
                'keywords': keywords,
                'src': source,
            }

            save_to_vector_db(embedding=embedding, metadata=metadata, title=title, desc=desc)

        doc_count += 1
        if doc_count > 25:
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
