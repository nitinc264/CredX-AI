# file: resume_parser.py

import os
import json
try:
    import fitz
except ImportError:
    fitz = None
try:
    import google.generativeai as genai
except ImportError:
    genai = None

class ResumeParser:
    def __init__(self, api_key):
        if fitz is None:
            print("WARNING: PyMuPDF (fitz) is not installed. PDF parsing will be disabled.")
        if genai is None:
            print("WARNING: Google Generative AI SDK is not installed. Resume parsing will be disabled.")
        self.api_key = api_key

    def _extract_text_from_pdf(self, file_stream):
        if not fitz:
            return None
        try:
            doc = fitz.open(stream=file_stream.read(), filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            return text
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return None

    def _analyze_text_with_llm(self, text):
        if not self.api_key or self.api_key == "YOUR_API_KEY_HERE" or not genai:
            return {"error": "AI client not configured in app.py."}

        prompt = f"""
        Analyze the following resume text and extract the following information in a pure JSON format:
        - "skills": A list of technical and soft skills found in the resume.
        - "titles": A list of potential job titles for the candidate based on their experience.
        - "locations": A list of preferred work locations, if mentioned.
        - "industries": A list of industries the candidate has experience in.
        Return only the raw JSON object, without any markdown formatting. Here is the resume text:
        """
        
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            generation_config = genai.types.GenerationConfig(response_mime_type="application/json")
            
            response = model.generate_content([prompt, text], generation_config=generation_config)
            
            return json.loads(response.text)
        except Exception as e:
            print(f"Error calling Gemini API in ResumeParser: {e}")
            return {"error": "Failed to analyze resume with AI."}

    def parse(self, file):
        if not fitz or not genai:
            return {"error": "A required library is not installed on the server."}
        text = self._extract_text_from_pdf(file)
        if not text:
            return {"error": "Could not extract text from the resume PDF."}
        return self._analyze_text_with_llm(text)
