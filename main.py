import chromadb
import uuid
from crawlers.crawlers import fsgeodata


def main():
    # chroma_client = chromadb.Client()
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    collection = chroma_client.get_or_create_collection(name="my_collection")

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
    
    results = collection.query(
        query_texts=["This is a query document about SilvReforestation"], # Chroma will embed this for you
        n_results=5 # how many results to return
    )
    
    # print(results)
    for r in results["documents"]:
        print(r)
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
