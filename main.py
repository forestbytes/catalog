import os

# import json
import psycopg2
from dotenv import load_dotenv
import click
from helpers.db import empty_documents_table, count_documents
from crawlers import FSGeodataHarvester, DataHubHarvester, RDAHarvester

# from typing import List
# from sentence_transformers import SentenceTransformer
# from langchain_text_splitters import (
#     RecursiveCharacterTextSplitter,
# )

# # from harvester import (
# #     _harvest_datahub,
# #     _harvest_fsgeodata,
# #     _harvest_rda,
# # )
# from schema import USFSDocument

load_dotenv()

# def save_to_vector_db(embedding, metadata, title="", desc=""):
#     with psycopg2.connect(pg_connection_string) as conn:
#         try:
#             cur = conn.cursor()
#             cur.execute(
#                 "INSERT INTO documents (doc_id, chunk_type, chunk_index, chunk_text, embedding, title, description, keywords, data_source) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
#                 (
#                     metadata["doc_id"],
#                     metadata["chunk_type"],
#                     metadata["chunk_index"],
#                     metadata["chunk_text"],
#                     embedding.tolist(),
#                     title,
#                     desc,
#                     metadata["keywords"],
#                     metadata["src"],
#                 ),
#             )
#         except psycopg2.errors.UniqueViolation as e:
#             print(f"IntegrityError: {e}, doc_id: {metadata['doc_id']}")
#             conn.rollback()

#         cur.close()
#         conn.commit()

# def load_usfs_docs_into_postgres(docs):
#     model = SentenceTransformer("all-MiniLM-L6-v2")

#     recursive_text_splitter = RecursiveCharacterTextSplitter(
#         chunk_size=65, chunk_overlap=0
#     )  # ["\n\n", "\n", " ", ""] 65,450

#     for fsdoc in docs:
#         title = fsdoc.title
#         description = fsdoc.description
#         keywords = ",".join(kw for kw in fsdoc.keywords) or []
#         combined_text = (
#             f"Title: {title}\nDescription: {description}\nKeywords: {keywords}"
#         )

#         chunks = recursive_text_splitter.create_documents([combined_text])
#         for idx, chunk in enumerate(chunks):
#             metadata = {
#                 "doc_id": fsdoc.id,  # or fsdoc.doc_id if that's the field name
#                 "chunk_type": "title+description+keywords",
#                 "chunk_index": idx,
#                 "chunk_text": chunk.page_content,
#                 "title": fsdoc.title,
#                 "description": fsdoc.description,
#                 "keywords": fsdoc.keywords,
#                 "src": fsdoc.src,  # or another source identifier
#             }

#             embedding = model.encode(chunk.page_content)

#             save_to_vector_db(
#                 embedding=embedding,
#                 metadata=metadata,
#                 title=fsdoc.title,
#                 desc=fsdoc.description,
#             )

os.chdir(os.path.dirname(os.path.abspath(__file__)))

fsgeodata = FSGeodataHarvester()
datahub = DataHubHarvester()
rda = RDAHarvester()


@click.group()
def cli():
    """Command line interface for managing USFS documents."""
    pass


@cli.command()
def clear_documents():
    """Clear the documents table in the database."""
    empty_documents_table()
    print("Documents table cleared.")


@cli.command()
def document_count():
    """Count the number of documents in the documents table."""

    doc_count = count_documents()
    print(f"Total documents in the vector database: {doc_count}")


@cli.command()
# @click.argument('json_path', type=click.Path(exists=True))
def download_usfs_fsgeodata():
    """Download USFS documents from a JSON file."""

    print("Downloading USFS documents from FS Geodata...")
    count = fsgeodata.download_metadata_files()
    print(f"Downloaded {count} metadata files from FS Geodata.")


@cli.command()
def download_usfs_datahub():
    """Download USFS documents from DataHub."""

    print("Downloading USFS documents from DataHub...")
    datahub.download_metadata_files()
    print(f"Downloaded metadata file from DataHub.")


@cli.command()
def download_usfs_rda():
    """Download USFS documents from RDA."""

    print("Downloading USFS documents from RDA...")
    rda.download_metadata_files()
    print(f"Downloaded metadata file from RDA.")


# json_path = "./tmp/usfs_docs.json"
# fsdocs = load_documents_from_json(json_path)
# load_usfs_docs_into_postgres(fsdocs)


if __name__ == "__main__":
    cli()
