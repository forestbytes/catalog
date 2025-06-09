import chromadb
import uuid
from crawlers.crawlers import fsgeodata


def main():
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    collection = chroma_client.get_or_create_collection(name="my_collection")

    results = collection.query(
        query_texts=["This is a query document about SilvReforestation"],
        n_results=5
    )
    
    for r in results["documents"]:
        print(r)

if __name__ == "__main__":
    main()