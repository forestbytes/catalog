# import chromadb
# import uuid

import openai
import numpy as np
import psycopg2
from crawlers.crawlers import fsgeodata
from dotenv import load_dotenv
import os
from sentence_transformers import SentenceTransformer
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

def get_embedding(text):

    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(text)
    return(embeddings.tolist())

def main():
    items = fsgeodata()
    for item in items:
        item["embedding"] = get_embedding(item["description"])

    # load_fsgeodatainto_postgres()
    # chroma_client = chromadb.Client()
    # chroma_client = chromadb.PersistentClient(path="./chroma_db")
    # collection = chroma_client.get_or_create_collection(name="my_collection")

    # assets = fsgeodata()
    # document_list = []
    # id_list = []
    
    # for asset in assets:
    #     document_list.append(asset["description"])
    #     id_list.append(asset["id"])
    
    # collection.add(
    #     documents=document_list,
    #     ids=id_list
    # )
    
    # results = collection.query(
    #     query_texts=["This is a query document about SilvReforestation"], # Chroma will embed this for you
    #     n_results=5 # how many results to return
    # )
    
    # # print(results)
    # for r in results["documents"]:
    #     print(r)
    # query_tests(collection=collection)

#     # Generate a UUID4 (random UUID)
#     # unique_id = uuid.uuid4()
#     # print(unique_id)

#     collection.add(
#         documents=[
#             "This is a document about pineapple",
#             "This is a document about oranges",
#             "This is a document about snow",
#             "This is a document about Larry Bird"
#         ],
#         ids=[str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())]
#     )

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
