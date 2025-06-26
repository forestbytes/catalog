import streamlit as st
import chromadb

collection_name = "usfs_collection"
chroma_client = chromadb.HttpClient(host='localhost', port=8000)
collection = chroma_client.get_or_create_collection(name=collection_name)

def query_collection(collection, query_texts, n_results=5):
    """
    Queries the collection with the given texts and returns the results.
    """

    results = collection.query(
        query_texts=query_texts,  # Chroma will embed this for you
        n_results=n_results  # how many results to return
    )
    return results

st.title("🌲 USFS Data Catalog")
st.write("Ask me anything about the US Forest Service data! ")


quesiton = None
with st.form("user_input_form", clear_on_submit=True):
    question = st.text_input(
        "Enter your question here:",
        key="user_input",
        placeholder="Where can I find wildfire data?",
    )
    st.form_submit_button("Search")

if question:
    # Display the user's question
    st.write(f"You asked: {question}")
    st.write("Processing your question...")
    results = query_collection(
        collection,
        query_texts=[question],
        n_results=5
    )
    if not results["documents"] and len(results["documents"][0]) > 0:
        st.write("No results found for your question.")
    else:
        st.write("Here are some resources related to your question:")
        for i, doc in enumerate(results["documents"][0]):
            st.write(doc)
