#!/usr/bin/env python3

import os
import json
import re
import argparse
import logging
from typing import Dict, Optional

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    from pdfminer.high_level import extract_text as pdfminer_extract
except ImportError:
    pdfminer_extract = None

try:
    import pytesseract
    from PIL import Image
except ImportError:
    pytesseract = None
    Image = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    from jsonschema import validate, ValidationError
except ImportError:
    validate = None
    ValidationError = None

# JSON Schema for profile validation
PROFILE_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": ["string", "null"]},
        "email": {"type": ["string", "null"]},
        "phone": {"type": ["string", "null"]},
        "skills": {"type": "array", "items": {"type": "string"}},
        "experience_summary": {"type": "string"},
        "education": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "degree": {"type": ["string", "null"]},
                    "institution": {"type": ["string", "null"]},
                    "start_date": {"type": ["string", "null"]},
                    "end_date": {"type": ["string", "null"]}
                }
            }
        },
        "seniority_level": {
            "type": "string",
            "enum": ["Intern", "Entry", "Mid", "Senior", "Lead", "Manager", "Director", "Executive", "Unknown"]
        },
        "job_interests": {"type": "array", "items": {"type": "string"}},
        "raw_text": {"type": "string"},
        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0}
    },
    "required": ["skills", "experience_summary", "education", "seniority_level", "job_interests", "raw_text", "confidence"]
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_text_from_pdf(path: str) -> str:
    """Extract text from PDF using PyMuPDF."""
    if not fitz:
        raise ImportError("PyMuPDF not installed")
    
    try:
        doc = fitz.open(path)
        texts = []
        for page in doc:
            page_text = page.get_text("text")
            texts.append(page_text)
        raw = "\n".join(texts)
        doc.close()
        return raw
    except Exception as e:
        logger.error(f"PyMuPDF extraction failed: {e}")
        return ""

def fallback_extract_text(path: str) -> str:
    """Fallback text extraction using pdfminer and OCR."""
    # Try pdfminer first
    if pdfminer_extract:
        try:
            text = pdfminer_extract(path)
            if len(text.strip()) > 200:
                return text
        except Exception as e:
            logger.warning(f"pdfminer extraction failed: {e}")
    
    # OCR fallback
    if pytesseract and Image and fitz:
        try:
            doc = fitz.open(path)
            ocr_texts = []
            for page in doc:
                pix = page.get_pixmap(dpi=300)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                ocr_text = pytesseract.image_to_string(img)
                ocr_texts.append(ocr_text)
            doc.close()
            return "\n".join(ocr_texts)
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
    
    return ""

def clean_text(text: str) -> str:
    """Clean and normalize extracted text."""
    # Remove hyphenated line breaks
    text = re.sub(r"-\n", "", text)
    # Normalize multiple newlines
    text = re.sub(r"\n{2,}", "\n\n", text)
    # Merge single-line breaks within paragraphs
    text = re.sub(r"(?<=\w)\n(?=[a-z0-9])", " ", text)
    # Remove excessive whitespace
    text = re.sub(r" {2,}", " ", text)
    return text.strip()

def call_gemini(raw_text: str, api_key: str) -> Dict:
    """Call Gemini API to extract structured profile data."""
    if not genai or not api_key:
        raise ValueError("Gemini API not configured")
    
    system_prompt = """You are an expert resume parser and normalizer. Given a block of resume text, return a JSON object that strictly conforms to the provided schema. Do not include any commentary or extra fields. If a value is unavailable or uncertain, use null. For lists, provide empty list if none. Ensure fields are normalized and concise. Provide a confidence score between 0.0 and 1.0 estimating extraction reliability."""
    
    user_prompt = f"""Extract the following profile JSON from the resume text below. Output only valid JSON that matches this schema:

{{
  "name": string|null,
  "email": string|null,
  "phone": string|null,
  "skills": [string],
  "experience_summary": string,
  "education": [{{"degree": string|null, "institution": string|null, "start_date": string|null, "end_date": string|null}}],
  "seniority_level": "Intern|Entry|Mid|Senior|Lead|Manager|Director|Executive|Unknown",
  "job_interests": [string],
  "raw_text": string,
  "confidence": number
}}

Resume text starts after the line "=== RESUME TEXT ===". Treat line breaks as part of raw_text. Normalize technologies (e.g., "PyTorch", "pytorch" -> "PyTorch"). For dates, prefer YYYY-MM or YYYY; if only year present, use YYYY. For seniority, infer from job titles, years of experience, and language in the resume. For job_interests, infer likely roles or domains (e.g., "ML Engineer", "Backend Developer", "Product Manager").

=== RESUME TEXT ===
{raw_text}
=== END ==="""
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        response = model.generate_content(
            f"{system_prompt}\n\n{user_prompt}",
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json",
                max_output_tokens=800
            )
        )
        
        result = json.loads(response.text)
        result["raw_text"] = raw_text  # Ensure raw_text is included
        return result
        
    except Exception as e:
        logger.error(f"Gemini API call failed: {e}")
        # Return fallback structure
        return {
            "name": None,
            "email": None,
            "phone": None,
            "skills": [],
            "experience_summary": "Failed to parse resume content",
            "education": [],
            "seniority_level": "Unknown",
            "job_interests": [],
            "raw_text": raw_text,
            "confidence": 0.0
        }

def validate_profile(profile: Dict) -> Dict:
    """Validate and normalize profile data."""
    if validate and ValidationError:
        try:
            validate(instance=profile, schema=PROFILE_SCHEMA)
        except ValidationError as e:
            logger.warning(f"Schema validation failed: {e}")
    
    # Ensure required fields exist with defaults
    defaults = {
        "name": None,
        "email": None,
        "phone": None,
        "skills": [],
        "experience_summary": "",
        "education": [],
        "seniority_level": "Unknown",
        "job_interests": [],
        "raw_text": "",
        "confidence": 0.0
    }
    
    for key, default_value in defaults.items():
        if key not in profile:
            profile[key] = default_value
    
    # Ensure confidence is within bounds
    profile["confidence"] = max(0.0, min(1.0, profile.get("confidence", 0.0)))
    
    return profile

def parse_resume(path: str, api_key: str = None) -> Dict:
    """Main function to parse resume and return structured profile."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Resume file not found: {path}")
    
    # Extract text
    raw_text = extract_text_from_pdf(path)
    
    # Use fallback if extraction failed or yielded too little text
    if len(raw_text.strip()) < 200:
        logger.info("Using fallback extraction method")
        raw_text = fallback_extract_text(path)
    
    if len(raw_text.strip()) < 50:
        raise ValueError("Could not extract meaningful text from PDF")
    
    # Clean text
    cleaned_text = clean_text(raw_text)
    
    # Get API key from environment if not provided
    if not api_key:
        api_key = os.environ.get("GOOGLE_API_KEY")
    
    if not api_key:
        logger.warning("No API key provided, returning basic extraction")
        return {
            "name": None,
            "email": None,
            "phone": None,
            "skills": [],
            "experience_summary": "API key required for full parsing",
            "education": [],
            "seniority_level": "Unknown",
            "job_interests": [],
            "raw_text": cleaned_text,
            "confidence": 0.1
        }
    
    # Call Gemini API
    profile = call_gemini(cleaned_text, api_key)
    
    # Validate and normalize
    profile = validate_profile(profile)
    
    return profile

class ResumeParser:
    """Legacy class for backward compatibility."""
    def __init__(self, api_key):
        self.api_key = api_key
        if fitz is None:
            logger.warning("PyMuPDF (fitz) is not installed. PDF parsing will be disabled.")
        if genai is None:
            logger.warning("Google Generative AI SDK is not installed. Resume parsing will be disabled.")

    def _extract_text_from_pdf(self, file_stream):
        """Legacy method for file stream extraction."""
        if not fitz:
            return None
        try:
            doc = fitz.open(stream=file_stream.read(), filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return None

    def _analyze_text_with_llm(self, text):
        """Legacy method for LLM analysis."""
        if not self.api_key or self.api_key == "YOUR_API_KEY_HERE" or not genai:
            return {"error": "AI client not configured in app.py."}
        
        try:
            profile = call_gemini(text, self.api_key)
            return profile
        except Exception as e:
            logger.error(f"Error calling Gemini API in ResumeParser: {e}")
            return {"error": "Failed to analyze resume with AI."}

    def parse(self, file):
        """Legacy parse method for file streams."""
        if not fitz or not genai:
            return {"error": "A required library is not installed on the server."}
        text = self._extract_text_from_pdf(file)
        if not text:
            return {"error": "Could not extract text from the resume PDF."}
        return self._analyze_text_with_llm(text)

def main():
    """CLI interface."""
    parser = argparse.ArgumentParser(description="Resume Parser CLI")
    parser.add_argument("command", choices=["parse"], help="Command to execute")
    parser.add_argument("pdf_path", help="Path to PDF resume")
    parser.add_argument("--out", help="Output JSON file path")
    parser.add_argument("--api-key", help="Gemini API key (or set GOOGLE_API_KEY env var)")
    
    args = parser.parse_args()
    
    if args.command == "parse":
        try:
            profile = parse_resume(args.pdf_path, args.api_key)
            
            if args.out:
                with open(args.out, 'w') as f:
                    json.dump(profile, f, indent=2)
                print(f"Profile saved to {args.out}")
            else:
                print(json.dumps(profile, indent=2))
                
        except Exception as e:
            logger.error(f"Failed to parse resume: {e}")
            return 1
    
    return 0

if __name__ == "__main__":
    exit(main())