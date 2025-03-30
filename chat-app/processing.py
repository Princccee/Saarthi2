import os
import requests
from dotenv import load_dotenv
from gradio_client import Client
from deep_translator import GoogleTranslator
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

# Ensure consistent language detection
DetectorFactory.seed = 0

# Load environment variables
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# Initialize Gradio Client
client = Client("https://e5abe742dca62081bb.gradio.live/")

SUPPORTED_LANGUAGES = GoogleTranslator().get_supported_languages(as_dict=True)

def detect_language(text):
    """Detects the language of a given text."""
    try:
        return detect(text)
    except LangDetectException:
        return "en"  # Default to English if detection fails
    
def translate_text(text, original_language=None):
    """Translates text to English using Gradio API."""
    # src_lang = detect_language(text)  # Detect the source language
    target_language = "English"  # Always translate to English

    try:
        result = client.predict(
            text=text,
            src_lang=original_language,
            tgt_lang=target_language,
            api_name="/translate_text"
        )
        return result
    except Exception as e:
        print(f"Translation error: {e}")
        return text  # Fallback: Return original text if translation fails
 

def detect_and_translate_to_english(text):
    """Detects the language and translates to English."""
    try:
        detected_language = detect(text)
        if detected_language not in SUPPORTED_LANGUAGES:
            detected_language = 'en'

        translated_text = text if detected_language == 'en' else GoogleTranslator(source=detected_language, target='en').translate(text)
    except LangDetectException:
        detected_language, translated_text = 'en', text

    return translated_text, detected_language

def translate_to_original_language(text, original_language):
    """Translates text back to the original language."""
    try:
        if original_language not in SUPPORTED_LANGUAGES:
            original_language = 'en'

        return GoogleTranslator(source='en', target=original_language).translate(text)
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def get_gemini_response(prompt):
    """Generates a response using Gemini-Pro."""
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    params = {"key": GOOGLE_API_KEY}
    
    response = requests.post(API_URL, headers=headers, params=params, json=data)

    if response.status_code == 200:
        try:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, TypeError):
            return "Invalid response format from API."
    else:
        return f"Error: {response.status_code}, {response.text}"

def process_text(user_text):
    """Processes the input text through translation and generation pipeline."""

    original_language = detect_language(user_text)
    print(f"Original Language: {original_language}")

    # Translate to English
    translated_text = translate_text(user_text, original_language)
    # translated_text, original_language = detect_and_translate_to_english(user_text)
    gemini_response = get_gemini_response(translated_text)
    return translate_to_original_language(gemini_response, original_language)
