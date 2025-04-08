import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from processing import process_text_with_gemini

# Load environment variables
load_dotenv()

# Update paths to access static and template folders outside this file
app = Flask(__name__, static_folder='../static', template_folder='../templates')
CORS(app)

# Route to serve the frontend
@app.route('/')
def index():
    return render_template('index.html')

# API route to process user text
@app.route('/process', methods=['POST'])
def process():
    data = request.json
    user_text = data.get("text", "")

    if not user_text:
        return jsonify({"error": "No text provided"}), 400

    response_text = process_text_with_gemini(user_text)  # using Google Translate logic or Gemini
    # response_text = process_text_with_ai4b(user_text)  # (optional) switch logic

    return jsonify({"response": response_text})

if __name__ == '__main__':
    app.run(debug=True)
