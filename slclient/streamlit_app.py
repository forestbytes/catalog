import streamlit as st

st.title("🌲 USFS Catalog")
st.write("Ask me anything about the US Forest Service data! ")

quesiton = None
with st.form("user_input_form", clear_on_submit=True):
    # Create a text input field for user questions
    # The key is used to uniquely identify the input field
    # The placeholder provides a hint to the user about what to enter
    question = st.text_input(
        "Enter your question here:",
        key="user_input",
        placeholder="Where can I find wildfire data?",
    )
    st.form_submit_button("Search")

if question:
    # Display the user's question
    st.write(f"You asked: {question}")

    # Here you would typically call a function to process the question
    # and return relevant information from the USFS data.
    # For now, we will just simulate a response.
    st.write("Processing your question...")

    # Simulated response
    st.write("Here are some resources related to your question:")

    mock_results = [
        "1. Fake search result 1",
        "2. Fake search result 2",
        "3. Fake search result 3",
        "4. Fake search result 4",
        "5. Fake search result 5",
    ]

    for result in mock_results:
        st.write(result)
