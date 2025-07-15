import os
import json
import psycopg2
from typing import List
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter, CharacterTextSplitter
from rich import print as rprint

from harvester import (
    _harvest_datahub,
    _harvest_fsgeodata,
    _harvest_rda,
    merge_docs,
    find_duplicate_documents,
)
from schema import USFSDocument

dbname = os.environ.get("PG_DBNAME") or "postgres"
dbuser = os.environ.get("POSTGRES_USER")
dbpass = os.environ.get("POSTGRES_PASSWORD")

pg_connection_string = f"dbname={dbname} user={dbuser} password={dbpass} host='0.0.0.0'"

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
                    desc,
                    metadata['keywords'],
                    metadata['src']
                )
            )
        except psycopg2.errors.UniqueViolation as e:
            print(f"IntegrityError: {e}, doc_id: {metadata['doc_id']}")
            conn.rollback()

        cur.close()
        conn.commit()


def load_documents_from_json(json_path: str) -> List[USFSDocument]:
    with open(json_path, "r") as f:
        data = json.load(f)
    # If the JSON is a list of dicts:
    return [USFSDocument(**item) for item in data]

def count_docs():

    with psycopg2.connect(pg_connection_string) as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM documents")
        rec = cur.fetchone()
        cur.close()

        return rec[0] or None


def load_usfs_docs_into_postgres(docs):
    model = SentenceTransformer('all-MiniLM-L6-v2')

    recursive_text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 65,
        chunk_overlap=0
    ) # ["\n\n", "\n", " ", ""] 65,450

    for fsdoc in docs:
        title = fsdoc.title
        description = fsdoc.description
        keywords = ",".join(kw for kw in fsdoc.keywords) or []
        combined_text = f"Title: {title}\nDescription: {description}\nKeywords: {keywords}"

        chunks = recursive_text_splitter.create_documents([combined_text])
        for idx, chunk in enumerate(chunks):
            metadata = {
                'doc_id': fsdoc.id,  # or fsdoc.doc_id if that's the field name
                'chunk_type': 'title+description+keywords',
                'chunk_index': idx,
                'chunk_text': chunk.page_content,
                'title': fsdoc.title,
                'description': fsdoc.description,
                'keywords': fsdoc.keywords,
                'src': fsdoc.src  # or another source identifier
            }

            embedding = model.encode(chunk.page_content)

            save_to_vector_db(
                embedding=embedding,
                metadata=metadata,
                title=fsdoc.title,
                desc=fsdoc.description
            )



def main():

    doc_count = count_docs()
    print(f"USFS Catalog document count: {doc_count}")

    # empty_documents_table()

    json_path = "./tmp/usfs_docs.json"
    fsdocs = load_documents_from_json(json_path)
    load_usfs_docs_into_postgres(fsdocs)



if __name__ == "__main__":
    main()

"""
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)

for doc in fsdocs:
    # Combine fields into one string
    combined_text = f"Title: {doc.title}\nDescription: {doc.description}\nKeywords: {', '.join(doc.keywords or [])}"
    # Chunk the combined text
    chunks = text_splitter.create_documents([combined_text])
    for chunk in chunks:
        embedding = model.encode(chunk.page_content)
        # Save embedding and metadata (e.g., doc_id, chunk_index, etc.)
        # save_to_vector_db(embedding, metadata, title=doc.title, desc=doc.description)
"""
