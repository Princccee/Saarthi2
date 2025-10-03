import os
import io
import csv
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from dotenv import load_dotenv
from processing import process_text_with_gemini, process_text_with_ai4b, process_row

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

    # response_text = process_text_with_gemini(user_text)
    response_text = process_text_with_ai4b(user_text)

    return jsonify({"response": response_text})

@app.route('/process_csv', methods=['POST'])
def process_csv():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty file name"}), 400

    # Read uploaded CSV
    stream = io.StringIO(file.stream.read().decode("utf-8"))
    reader = csv.DictReader(stream)
    rows = list(reader)

    updated_rows = []
    for row in rows:
        ques = row.get("question", "")
        context = row.get("context", "")
        lang = row.get("lang", "en")

        response_text = process_row(ques, context, lang)
        row["response"] = response_text  # append new column
        updated_rows.append(row)

    # Save updated CSV to project root
    output_file = os.path.join(os.getcwd(), "processed_output.csv")
    fieldnames = reader.fieldnames + ["response"]
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)

    return jsonify({"message": f"✅ File processed and saved as {output_file}"})

if __name__ == '__main__':
    app.run(debug=True)