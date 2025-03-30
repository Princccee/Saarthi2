import streamlit as st
import requests

st.set_page_config(page_title="Chatbot", page_icon=":robot:", layout="wide")
st.title("🤖 Chatbot")

API_ENDPOINT = "http://127.0.0.1:5000/process"

# User Input
user_text = st.text_area("Enter your prompt....")

if st.button("Send"):
    if user_text:
        st.chat_message("user").markdown(user_text)

        response = requests.post(API_ENDPOINT, json={"text": user_text})
        
        if response.status_code == 200:
            bot_response = response.json().get("response", "No response")
        else:
            bot_response = f"Error: {response.status_code}, {response.text}"

        with st.chat_message("assistant"):
            st.markdown(bot_response)
