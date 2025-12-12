# file: story_generator.py

import os
import json
try:
    import google.generativeai as genai
except ImportError:
    genai = None

class StoryGenerator:
    def __init__(self, api_key):
        if genai is None:
            print("WARNING: Google Generative AI SDK is not installed. Story generation will be disabled.")
        self.api_key = api_key

    def _construct_prompt(self, candidate_prefs, job_details):
        c_skills = ", ".join(candidate_prefs.get('skills', []))
        j_title = job_details.get('title', 'N/A')
        j_skills = ", ".join(job_details.get('required_skills', []))

        prompt = f"""
        You are an expert career coach. Write a concise, encouraging, 2-sentence "Match Story" explaining why this job fits the candidate.
        Candidate Skills: {c_skills}
        Job Title: {j_title}
        Required Skills: {j_skills}
        Focus on connecting the candidate's skills to the job's requirements.
        """
        return prompt

    def generate_story(self, candidate_prefs, job_details):
        if not self.api_key or self.api_key == "YOUR_API_KEY_HERE" or not genai:
            return "Story generation is unavailable. Check API key in app.py."

        prompt = self._construct_prompt(candidate_prefs, job_details)
        
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error calling Gemini API for story generation: {e}")
            return f"This role aligns well with your skills in {', '.join(job_details.get('required_skills', [])[:2])}."
