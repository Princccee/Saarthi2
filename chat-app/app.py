import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from processing import process_text_with_ai4b, process_text_with_gemini

# Load environment variables
load_dotenv()

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    user_text = data.get("text", "")

    if not user_text:
        return jsonify({"error": "No text provided"}), 400

    response_text = process_text_with_gemini(user_text) # using google trans
    # response_text = process_text_with_ai4b(user_text)  # using ai4b

    return jsonify({"response": response_text})

if __name__ == '__main__':
    app.run(debug=True)
