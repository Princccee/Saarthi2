import streamlit as st
import requests
import speech_recognition as sr

st.set_page_config(page_title="Chatbot", page_icon=":robot:", layout="wide")
st.title("🤖 Chatbot")

API_ENDPOINT = "http://127.0.0.1:5000/process"

recognizer = sr.Recognizer()

def recognize_speech():
    """Captures speech input and converts it to text."""
    with sr.Microphone() as source:
        st.info("🎙️ Listening... Speak now.")
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return "Could not understand the audio."
        except sr.RequestError:
            return "Speech recognition service unavailable."

# Initialize session state for user input
if "user_text" not in st.session_state:
    st.session_state.user_text = ""

# User Input (Text Area)
st.session_state.user_text = st.text_area("Enter your prompt....", value=st.session_state.user_text)

# Mic button for speech input
if st.button("🎤 Speak"):
    recognized_text = recognize_speech()
    if recognized_text:
        st.session_state.user_text = recognized_text  # Update the text area
        st.experimental_rerun()  # Refresh the UI to reflect changes

# Send button
if st.button("Send"):
    if st.session_state.user_text:
        st.chat_message("user").markdown(st.session_state.user_text)

        response = requests.post(API_ENDPOINT, json={"text": st.session_state.user_text})
        
        if response.status_code == 200:
            bot_response = response.json().get("response", "No response")
        else:
            bot_response = f"Error: {response.status_code}, {response.text}"

        with st.chat_message("assistant"):
            st.markdown(bot_response)
