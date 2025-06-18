# import uuid

import openai
import numpy as np
import psycopg2
from crawlers.crawlers import fsgeodata
from dotenv import load_dotenv
import os
import chromadb
# from sentence_transformers import SentenceTransformer
# from langchain.embeddings import HuggingFaceEmbeddings

load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = "postgres" # os.getenv("POSTGRES_DB")
DB_URL = f"postgres://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost:5432/{POSTGRES_DB}"
OPEN_AI_API_KEY = os.getenv("OPENAI_API_KEY")

def load_fsgeodatainto_postgres(items):
    

    for item in items:
        with psycopg2.connect(DB_URL) as conn:
            description = item["description"].replace("'", "''")  # Escape single quotes for SQL
            url = item["metadata_source_url"]
            sql = f"INSERT INTO items (description, url) VALUES ('{description}', '{url}')"
            try:
                cursor = conn.cursor()
                cursor.execute(sql)
                conn.commit()
            except psycopg2.Error as e:
                print(f"Error inserting item: {e}")


# def get_embedding(text):

#     model = SentenceTransformer('all-MiniLM-L6-v2')
#     embeddings = model.encode(text)
#     return(embeddings.tolist())


def empty_collection(collection):
    """
    Deletes all documents in the specified collection.
    """
    doc_ids = collection.get()["ids"]
    if doc_ids:
        collection.delete(ids=doc_ids)
        print(f"Deleted {len(doc_ids)} documents from the collection.")
    else:
        print("No documents to delete in the collection.")


def populate_collection(collection):
    """
    Populates the collection with sample documents.
    """
    
    assets = fsgeodata()
    document_list = []
    id_list = []
    for asset in assets:
        document_list.append(asset["description"])
        id_list.append(str(asset["id"]))

        collection.add(
            documents=document_list,
            ids=id_list
        )
    count = collection.count()
    print(f"Collection populated with {count} documents.")


def query_collection(collection, query_texts, n_results=5):
    """
    Queries the collection with the given texts and returns the results.
    """
    results = collection.query(
        query_texts=query_texts,  # Chroma will embed this for you
        n_results=n_results  # how many results to return
    )
    return results


def main():
    collection_name = "usfs_collection"
    chroma_client = chromadb.HttpClient(host='0.0.0.0', port=8000)
    collection = chroma_client.get_or_create_collection(name=collection_name)
    
    assets = fsgeodata()
    count = 0
    for asset in assets:
        if "fire" in asset["description"].lower():
            count += 1
    print(f"Found {count} assets related to fire.")

    # empty_collection(collection)
    # populate_collection(collection)
    
    results = query_collection(
        collection,
        query_texts=["Which data set in the collection have time series data related to fire?"],
        n_results=100
    )

    count = 0
    documents = results["documents"][0]
    for doc in documents:
        if "fire" in doc.lower():
            print(doc)
            count += 1
            exit(0)
    print(f"Found {count} documents related to fire in the results.")

    # print(f"{results.count()} documents found.")
    # for r in results["documents"]:
    #     print(r)


    # load_fsgeodatainto_postgres()
    # chroma_client = chromadb.Client()
    # chroma_client = chromadb.PersistentClient(path="./chroma_db")
    # collection = chroma_client.get_or_create_collection(name="my_collection")

    # )
    
    # # print(results)
    # for r in results["documents"]:
    #     print(r)
    # query_tests(collection=collection)


#     query_tests(collection=collection)


# def show_results(results):
#     print(results.keys())
#     print(results["distances"])
#     # for d in results["documents"]:
#     #     print(d, dir(d))


# def query_tests(collection):
#     n_results = 5

#     results = collection.query(
#         query_texts=["This is a query document about hawaii"], # Chroma will embed this for you
#         n_results=n_results # how many results to return
#     )
    
#     show_results(results)
    
#     results = collection.query(
#         query_texts=["This is a query document about florida"], # Chroma will embed this for you
#         n_results=n_results # how many results to return
#     )
    
#     show_results(results)

#     results = collection.query(
#         query_texts=["This is a query document about nebraska"], # Chroma will embed this for you
#         n_results=n_results # how many results to return
#     )
    
#     show_results(results)

#     results = collection.query(
#         query_texts=["This is a query document about sports"], # Chroma will embed this for you
#         n_results=n_results # how many results to return
#     )
    
#     show_results(results)

if __name__ == "__main__":
    main()
