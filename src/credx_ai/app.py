# file: app.py

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from .matching_engine import Recommender
from .resume_parser import ResumeParser
import os
try:
    import google.generativeai as genai
except ImportError:
    genai = None

app = Flask(__name__)
CORS(app)

DATA_FILE_PATH = os.path.join('data', 'jobs.csv')

API_KEY = os.environ.get("GOOGLE_API_KEY")

if API_KEY and genai:
    try:
        genai.configure(api_key=API_KEY)
        print("Google Generative AI configured successfully.")
    except Exception as e:
        print(f"Error configuring Google AI: {e}")
else:
    print("WARNING: API key not set in app.py or 'google-generativeai' is not installed.")

print("Initializing the recommendation engine...")
recommender = Recommender(DATA_FILE_PATH, api_key=API_KEY)
resume_parser = ResumeParser(api_key=API_KEY)
print("Recommendation engine initialized successfully.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        request_data = request.get_json()
        if not request_data:
            return jsonify({"error": "Invalid JSON payload"}), 400
        recommendations = recommender.get_recommendations(request_data)
        return jsonify(recommendations)
    except Exception as e:
        print(f"An error occurred in /recommend: {e}", flush=True)
        return jsonify({"error": "An internal server error occurred."}), 500

@app.route('/parse_resume', methods=['POST'])
def parse_resume_route():
    if 'resume' not in request.files:
        return jsonify({"error": "No resume file provided."}), 400
    file = request.files['resume']
    if file.filename == '':
        return jsonify({"error": "No selected file."}), 400
    try:
        extracted_data = resume_parser.parse(file)
        return jsonify(extracted_data)
    except Exception as e:
        print(f"An error occurred in /parse_resume: {e}")
        return jsonify({"error": "Failed to parse the resume."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


