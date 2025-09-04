import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from processing import process_text_with_gemini

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
print("Loaded API Key:", api_key)

app = Flask(__name__, static_folder='../static', template_folder='../templates')
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    user_text = data.get("text", "")

    if not user_text:
        return jsonify({"error": "No text provided"}), 400

    response_text = process_text_with_gemini(user_text)

    return jsonify({"response": response_text})

if __name__ == '__main__':
    app.run(debug=True)