import os, json
import psycopg2
from dotenv import load_dotenv
from typing import List
from schema import USFSDocument

load_dotenv()


dbname = os.environ.get("PG_DBNAME") or "postgres"
dbuser = os.environ.get("POSTGRES_USER")
dbpass = os.environ.get("POSTGRES_PASSWORD")
pg_connection_string = f"dbname={dbname} user={dbuser} password={dbpass} host='0.0.0.0'"

def load_documents_from_json(json_path: str) -> List[USFSDocument]:
    with open(json_path, "r") as f:
        data = json.load(f)
    # If the JSON is a list of dicts:
    return [USFSDocument(**item) for item in data]


def empty_documents_table():
    """
    Deletes all records from the 'documents' table in the vector database and performs a full vacuum to reclaim storage if the deletion was successful.

    This function connects to the PostgreSQL database using the provided connection string, removes all entries from the 'documents' table, and commits the transaction. If the deletion is successful, it then performs a 'VACUUM FULL' operation on the table to optimize storage and performance.

    Raises:
        psycopg2.DatabaseError: If there is an error connecting to the database or executing the SQL commands.
    """

    result = None
    with psycopg2.connect(pg_connection_string) as conn:
        cur = conn.cursor()
        result = cur.execute("DELETE FROM documents")
        conn.commit()
        cur.close()

    if result:
        with psycopg2.connect(pg_connection_string) as conn:
            cur = conn.cursor()
            cur.execute("VACUUM FULL documents")
            conn.commit()
            cur.close()


def count_documents():
    """
    Counts the number of documents in the 'documents' table of the vector database.

    Returns:
        int: The count of documents in the table.
    """

    doc_count = None

    with psycopg2.connect(pg_connection_string) as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM documents")
        rec = cur.fetchone()
        doc_count = rec[0] if rec else 0
        cur.close()

    return doc_count


def save_to_vector_db(embedding, metadata, title="", desc=""):
    """
    Saves a document's embedding and metadata to the 'documents' table in the vector database.
    """

    with psycopg2.connect(pg_connection_string) as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO documents (doc_id, chunk_type, chunk_index, chunk_text, embedding, title, description, keywords, data_source) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    metadata["doc_id"],
                    metadata["chunk_type"],
                    metadata["chunk_index"],
                    metadata["chunk_text"],
                    embedding.tolist(),
                    title,
                    desc,
                    metadata["keywords"],
                    metadata["src"],
                ),
            )
        except psycopg2.errors.UniqueViolation as e:
            print(f"IntegrityError: {e}, doc_id: {metadata['doc_id']}")
            conn.rollback()

        cur.close()
        conn.commit()
