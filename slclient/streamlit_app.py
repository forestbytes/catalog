import streamlit as st

# with st.form("my_form"):
#    st.write("Inside the form")
#    my_number = st.slider('Pick a number', 1, 10)
#    my_color = st.selectbox('Pick a color', ['red','orange','green','blue','violet'])
#    st.form_submit_button('Submit my picks')

# # This is outside the form
# st.write(my_number)
# st.write(my_color)


st.title("🌲 USFS Catalog")
st.write(
    # "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
    "Ask me anything about the US Forest Service data! "
)

with st.form("user_input_form"):
    # Create a text input field for user questions
    # The key is used to uniquely identify the input field
    # The placeholder provides a hint to the user about what to enter
    question = st.text_input("Enter your question here:", key="user_input", placeholder="Where can I find wildfire data?")
    st.form_submit_button('Search')

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
    # st.write("- [Wildfire Data](https://www.fs.usda.gov/wildfire-data)")
    # st.write("- [Forest Service Reports](https://www.fs.usda.gov/reports)")