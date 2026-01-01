# file: resume_parser.py

import os
import json
import re
try:
    import fitz
except ImportError:
    fitz = None
try:
    import google.generativeai as genai
except ImportError:
    genai = None

# Common technical skills for fallback extraction
COMMON_SKILLS = [
    # Programming Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "go", "rust", "php", "swift", "kotlin", "scala",
    # Web Technologies
    "html", "css", "react", "angular", "vue", "node.js", "nodejs", "express", "django", "flask", "spring", "spring boot",
    "next.js", "nextjs", "nuxt", "svelte", "jquery", "bootstrap", "tailwind", "sass", "less",
    # Databases
    "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "oracle", "sqlite", "cassandra", "dynamodb",
    # Cloud & DevOps
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "jenkins", "terraform", "ansible", "ci/cd", "devops",
    # Data Science & ML
    "machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy", "data science",
    "nlp", "computer vision", "ai", "artificial intelligence",
    # Mobile
    "android", "ios", "react native", "flutter", "swift", "kotlin",
    # Other
    "git", "linux", "agile", "scrum", "rest", "api", "graphql", "microservices", "kafka", "rabbitmq",
    "jira", "confluence", "figma", "photoshop", "excel", "tableau", "power bi"
]

# Common job title keywords
TITLE_KEYWORDS = [
    "developer", "engineer", "architect", "manager", "lead", "senior", "junior", "analyst",
    "designer", "consultant", "administrator", "specialist", "director", "scientist", "intern"
]

class ResumeParser:
    def __init__(self, api_key):
        if fitz is None:
            print("WARNING: PyMuPDF (fitz) is not installed. PDF parsing will be disabled.")
        if genai is None:
            print("WARNING: Google Generative AI SDK is not installed. Resume parsing will use fallback mode.")
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

    def _extract_skills_fallback(self, text):
        """Extract skills using keyword matching as fallback."""
        text_lower = text.lower()
        found_skills = []
        
        for skill in COMMON_SKILLS:
            # Use word boundary matching for more accuracy
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                # Capitalize properly
                found_skills.append(skill.title() if len(skill) > 3 else skill.upper())
        
        return list(set(found_skills))  # Remove duplicates

    def _extract_titles_fallback(self, text):
        """Extract potential job titles from resume text."""
        text_lower = text.lower()
        lines = text.split('\n')
        titles = []
        
        for line in lines:
            line_lower = line.lower().strip()
            # Check if line contains title keywords
            for keyword in TITLE_KEYWORDS:
                if keyword in line_lower and len(line.strip()) < 50:
                    # Clean up the title
                    title = line.strip()
                    if title and title not in titles:
                        titles.append(title)
                        break
        
        return titles[:5]  # Return top 5 potential titles

    def _extract_locations_fallback(self, text):
        """Extract locations mentioned in the resume."""
        # Common Indian cities
        cities = [
            "mumbai", "delhi", "bangalore", "bengaluru", "hyderabad", "chennai", "kolkata",
            "pune", "ahmedabad", "jaipur", "lucknow", "kanpur", "nagpur", "indore", "thane",
            "bhopal", "visakhapatnam", "pimpri", "patna", "vadodara", "ghaziabad", "ludhiana",
            "agra", "nashik", "faridabad", "meerut", "rajkot", "varanasi", "srinagar", "noida",
            "gurgaon", "gurugram", "chandigarh", "coimbatore", "kochi", "thiruvananthapuram",
            "remote", "work from home", "wfh", "hybrid"
        ]
        
        text_lower = text.lower()
        found_locations = []
        
        for city in cities:
            if city in text_lower:
                found_locations.append(city.title())
        
        return list(set(found_locations))

    def _extract_industries_fallback(self, text):
        """Extract industries mentioned in the resume."""
        industries = [
            "technology", "it", "software", "finance", "banking", "healthcare", "education",
            "e-commerce", "ecommerce", "retail", "manufacturing", "consulting", "telecom",
            "media", "entertainment", "automotive", "pharma", "pharmaceutical", "insurance",
            "real estate", "logistics", "travel", "hospitality", "saas", "fintech", "edtech",
            "healthtech", "startup", "enterprise"
        ]
        
        text_lower = text.lower()
        found_industries = []
        
        for industry in industries:
            if industry in text_lower:
                found_industries.append(industry.upper() if len(industry) <= 3 else industry.title())
        
        return list(set(found_industries))

    def _analyze_text_with_llm(self, text):
        if not self.api_key or self.api_key == "YOUR_API_KEY_HERE" or not genai:
            return None  # Return None to trigger fallback

        # Check if it's not a valid Gemini key (OpenAI keys start with sk-)
        if self.api_key.startswith("sk-"):
            print("WARNING: Detected OpenAI API key. This app requires a Google Gemini API key.")
            return None

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
            return None  # Return None to trigger fallback

    def parse(self, file):
        if not fitz:
            return {"error": "PyMuPDF is not installed. Cannot parse PDF files."}
        
        text = self._extract_text_from_pdf(file)
        if not text:
            return {"error": "Could not extract text from the resume PDF."}
        
        # Try AI-powered parsing first
        result = self._analyze_text_with_llm(text)
        
        if result is not None:
            return result
        
        # Fallback to keyword-based extraction
        print("Using fallback resume parsing (keyword-based extraction)")
        skills = self._extract_skills_fallback(text)
        titles = self._extract_titles_fallback(text)
        locations = self._extract_locations_fallback(text)
        industries = self._extract_industries_fallback(text)
        
        # If we found some data, return it
        if skills or titles:
            return {
                "skills": skills,
                "titles": titles if titles else ["Software Developer"],  # Default title
                "locations": locations if locations else [],
                "industries": industries if industries else [],
                "note": "Parsed using keyword extraction. You can edit the fields above to refine."
            }
        
        return {"error": "Could not extract meaningful data from the resume. Please fill in your details manually."}
