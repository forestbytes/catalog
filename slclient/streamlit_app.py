import streamlit as st

st.title("🌲 USFS Catalog")
st.write(
    # "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
    "Ask me anything about the US Forest Service data! "
)

st.text_input("Enter your question here:", key="user_input", placeholder="Where can I find wildfire data?")