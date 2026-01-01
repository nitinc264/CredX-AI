import re
import math
from typing import List, Dict, Any

from .data_handler import DataHandler
from .semantic_matcher import SemanticMatcher
from .story_generator import StoryGenerator


class Recommender:
    """
    Job recommendation engine that matches candidate preferences to job listings.
    """
    def __init__(self, data_file_path: str, api_key: str = None):
        self.data_handler = DataHandler(data_file_path)
        self.semantic_matcher = SemanticMatcher()
        self.story_generator = StoryGenerator(api_key)

    def _calculate_skill_match(self, candidate_skills: List[str], job_skills: List[str]) -> float:
        """Calculate skill match score between candidate and job."""
        if not candidate_skills or not job_skills:
            return 0.0
        
        candidate_set = set(s.lower().strip() for s in candidate_skills)
        job_set = set(s.lower().strip() for s in job_skills)
        
        if not job_set:
            return 0.0
        
        # Direct matches
        direct_matches = candidate_set.intersection(job_set)
        direct_score = len(direct_matches) / len(job_set)
        
        # Semantic matching for non-matched skills
        unmatched_job_skills = job_set - direct_matches
        semantic_score = 0.0
        
        if unmatched_job_skills and self.semantic_matcher._model:
            for job_skill in unmatched_job_skills:
                max_sim = 0.0
                for cand_skill in candidate_set:
                    sim = self.semantic_matcher.get_similarity(cand_skill, job_skill)
                    max_sim = max(max_sim, sim)
                if max_sim > 0.5:  # threshold for semantic match
                    semantic_score += max_sim
            semantic_score = semantic_score / len(job_set) if job_set else 0.0
        
        return min(1.0, direct_score + semantic_score * 0.5)

    def _calculate_salary_match(self, candidate_salary: int, job_salary_range: List[int]) -> float:
        """Calculate salary match score."""
        if not job_salary_range or len(job_salary_range) < 2:
            return 1.0  # No salary info means no penalty
        
        min_salary, max_salary = job_salary_range[0], job_salary_range[1]
        
        if min_salary <= candidate_salary <= max_salary:
            return 1.0
        elif candidate_salary < min_salary:
            # Candidate wants less than minimum - still a good match
            return 1.0
        else:
            # Candidate wants more than maximum
            diff = candidate_salary - max_salary
            penalty = diff / max_salary if max_salary > 0 else 0
            return max(0.0, 1.0 - penalty)

    def _calculate_title_match(self, candidate_titles: List[str], job_title: str) -> float:
        """Calculate title match score using semantic similarity."""
        if not candidate_titles or not job_title:
            return 0.5  # Neutral score
        
        max_score = 0.0
        for title in candidate_titles:
            score = self.semantic_matcher.get_similarity(title, job_title)
            max_score = max(max_score, score)
        
        return max_score

    def _calculate_location_match(self, candidate_locations: List[str], job_location: str) -> float:
        """Calculate location match score."""
        if not candidate_locations or not job_location:
            return 1.0  # No preference means all locations are fine
        
        job_loc_lower = job_location.lower()
        for loc in candidate_locations:
            if loc.lower() in job_loc_lower or job_loc_lower in loc.lower():
                return 1.0
            if "remote" in loc.lower() and "remote" in job_loc_lower:
                return 1.0
        
        return 0.3  # Base score for non-matching locations

    def get_recommendations(self, request_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get job recommendations based on candidate preferences.
        
        Args:
            request_data: Dictionary containing:
                - preferences: Dict with skills, titles, locations, min_salary, industries
                - weights: Dict with weights for skill, title, location, salary, industry
        
        Returns:
            List of job recommendations with match scores and stories
        """
        # Extract preferences from request (frontend sends nested under 'preferences')
        preferences = request_data.get('preferences', request_data)
        candidate_skills = preferences.get('skills', [])
        candidate_titles = preferences.get('titles', [])
        candidate_locations = preferences.get('locations', [])
        candidate_salary = preferences.get('min_salary', preferences.get('salary', 0))
        candidate_industries = preferences.get('industries', [])
        weights = request_data.get('weights', {})
        
        # Default weights (matching frontend weight keys)
        w_skill = weights.get('skill', 30) / 100.0
        w_title = weights.get('title', 20) / 100.0
        w_location = weights.get('location', 15) / 100.0
        w_salary = weights.get('salary', 15) / 100.0
        w_industry = weights.get('industry', 20) / 100.0
        
        # Normalize weights
        total_weight = w_skill + w_title + w_location + w_salary + w_industry
        if total_weight > 0:
            w_skill /= total_weight
            w_title /= total_weight
            w_location /= total_weight
            w_salary /= total_weight
            w_industry /= total_weight
        
        jobs_df = self.data_handler.get_jobs()
        results = []
        
        for _, job in jobs_df.iterrows():
            job_dict = job.to_dict()
            job_skills = job_dict.get('required_skills', [])
            
            # Calculate component scores
            skill_score = self._calculate_skill_match(candidate_skills, job_skills)
            title_score = self._calculate_title_match(candidate_titles, job_dict.get('title', ''))
            location_score = self._calculate_location_match(candidate_locations, job_dict.get('location', ''))
            salary_score = self._calculate_salary_match(candidate_salary, job_dict.get('salary_range', [0, 0]))
            industry_score = self._calculate_industry_match(candidate_industries, job_dict.get('industry', ''))
            
            # Calculate weighted total score
            total_score = (
                skill_score * w_skill +
                title_score * w_title +
                location_score * w_location +
                salary_score * w_salary +
                industry_score * w_industry
            )
            
            # Generate match story
            story = self.story_generator.generate_story(preferences, job_dict)
            
            # Build skill validation details with match types
            skill_details = []
            for skill in job_skills:
                skill_lower = skill.lower().strip()
                candidate_skills_lower = [s.lower().strip() for s in candidate_skills]
                if skill_lower in candidate_skills_lower:
                    skill_details.append({'skill': skill, 'type': 'direct'})
                else:
                    # Check for semantic match
                    max_sim = 0.0
                    for cand_skill in candidate_skills:
                        sim = self.semantic_matcher.get_similarity(cand_skill, skill)
                        max_sim = max(max_sim, sim)
                    if max_sim > 0.5:
                        skill_details.append({'skill': skill, 'type': 'semantic'})
                    else:
                        skill_details.append({'skill': skill, 'type': 'none'})
            
            # Format salary range for display
            salary_range = job_dict.get('salary_range', [0, 0])
            if isinstance(salary_range, list) and len(salary_range) >= 2:
                salary_display = f"₹{salary_range[0]:,} - ₹{salary_range[1]:,}"
            else:
                salary_display = "Not specified"
            
            results.append({
                'job_id': job_dict.get('job_id', ''),
                'job_title': job_dict.get('title', ''),
                'company': job_dict.get('company', ''),
                'location': job_dict.get('location', ''),
                'match_score': round(total_score * 100, 2),
                'story': story,
                'breakdown': {
                    'Skills': round(skill_score * 100, 2),
                    'Title': round(title_score * 100, 2),
                    'Location': round(location_score * 100, 2),
                    'Salary': round(salary_score * 100, 2),
                    'Industry': round(industry_score * 100, 2)
                },
                'validation_details': {
                    'Skills': skill_details,
                    'Title': job_dict.get('title', ''),
                    'Location': job_dict.get('location', ''),
                    'Industry': job_dict.get('industry', ''),
                    'Salary': salary_display
                }
            })
        
        # Sort by match score descending
        results.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Return top 10 recommendations
        return results[:10]

    def _calculate_industry_match(self, candidate_industries: List[str], job_industry: str) -> float:
        """Calculate industry match score."""
        if not candidate_industries or not job_industry:
            return 1.0  # No preference means all industries are fine
        
        job_ind_lower = job_industry.lower()
        for ind in candidate_industries:
            if ind.lower() in job_ind_lower or job_ind_lower in ind.lower():
                return 1.0
        
        # Use semantic matching for industries
        max_sim = 0.0
        for ind in candidate_industries:
            sim = self.semantic_matcher.get_similarity(ind, job_industry)
            max_sim = max(max_sim, sim)
        
        if max_sim > 0.6:
            return max_sim
        
        return 0.3  # Base score for non-matching industries


def _tokenize(text: str) -> set:
    """
    Return a set of lowercase word tokens from text (alphanumeric), ignoring punctuation.
    """
    if not text:
        return set()
    return set(re.findall(r"\b\w+\b", text.lower()))


# Normalize score to 0-100
def normalize_score(score: float, min_score: float, max_score: float) -> float:
    """
    Normalize a raw score into the 0-100 range. If all scores are equal (max == min),
    return 100.0 so that equal candidates are scored at the top of the scale.
    """
    if max_score - min_score == 0:
        return 100.0
    return ((score - min_score) / (max_score - min_score)) * 100.0


# Simple semantic score using word overlap
def compute_semantic_score(text1: str, text2: str) -> float:
    """
    Semantic score = fraction of tokens in text1 that appear in text2.
    Returns value in [0.0, 1.0].

    Note: This is directional (text1 -> text2). For job-description -> candidate-summary
    this measures how much of the JD vocabulary appears in the candidate summary.
    """
    words1 = _tokenize(text1)
    words2 = _tokenize(text2)
    if not words1:
        return 0.0
    overlap = words1.intersection(words2)
    return len(overlap) / len(words1)


# Compute skill relevance score
def compute_skill_score(required: List[str], candidate_skills: List[str]) -> float:
    """
    Fraction of required skills that the candidate has. Returns value in [0.0, 1.0].

    If `required` is empty or None, returns 0.0 (no required skills means there's nothing
    to match and tests expect a 0.0 score).
    """
    # Follow test expectations: empty required list -> 0.0
    if not required:
        return 0.0
    required_set = set(s.lower() for s in required)
    candidate_set = set(s.lower() for s in (candidate_skills or []))
    matched = required_set.intersection(candidate_set)
    return len(matched) / len(required_set)


# Experience score
EXPERIENCE_LEVELS = {
    "intern": 0,
    "junior": 1,
    "mid": 2,
    "senior": 3,
    "lead": 4,
}


def compute_experience_score(required: str, candidate: str) -> float:
    """
    Returns experience fit score in [0.0, 1.0].
    If candidate level is >= required level -> 1.0
    Else returns candidate_level / required_level.
    If `required` is empty or None, treat the requirement as satisfied and return 1.0.
    If either level is unknown, returns 0.0.
    """
    # If no required experience is listed, consider it satisfied
    if not required:
        return 1.0

    if not candidate:
        return 0.0

    r = required.lower().strip()
    c = candidate.lower().strip()

    if r not in EXPERIENCE_LEVELS or c not in EXPERIENCE_LEVELS:
        return 0.0

    r_val = EXPERIENCE_LEVELS[r]
    c_val = EXPERIENCE_LEVELS[c]

    if r_val == 0:  # required is 'intern' or equivalent
        return 1.0 if c_val >= 0 else 0.0

    if c_val >= r_val:
        return 1.0

    return float(c_val) / float(r_val)


# Weighted score aggregation
def compute_weighted_score(semantic: float, skill: float, exp: float, weights: Dict[str, float]) -> float:
    """
    Compute a weighted aggregate of the three components.
    The provided weights are normalized so callers do not have to sum to 1.
    Accepts either 'skill_relevance' or 'skill' as the key for skill weight.
    Returns a raw score in [0.0, 1.0] (assuming inputs are in [0,1]).
    """
    # defaults
    if not weights:
        weights = {}

    w_sem = float(weights.get("semantic", 0.4))
    # accept either key historically used
    w_skill = float(weights.get("skill_relevance", weights.get("skill", 0.3)))
    w_exp = float(weights.get("experience", 0.3))

    total = w_sem + w_skill + w_exp
    if total <= 0:
        # fallback to sensible defaults
        w_sem, w_skill, w_exp = 0.4, 0.3, 0.3
        total = 1.0

    # normalize
    w_sem /= total
    w_skill /= total
    w_exp /= total

    return (semantic * w_sem) + (skill * w_skill) + (exp * w_exp)


def rank_candidates(job_description: str,
                    required_skills: List[str],
                    required_experience: str,
                    candidates: List[Dict[str, Any]],
                    weights: Dict[str, float]) -> List[Dict[str, Any]]:
    """
    Rank candidates and return a sorted list of result dicts (highest first).
    Each result dict contains:
      - candidate: original candidate dict
      - semantic: semantic score (0-1)
      - skills: skill match score (0-1)
      - experience: experience fit score (0-1)
      - raw_score: aggregated raw score (0-1)
      - score: normalized score (0-100)

    Notes:
      - If `weights` is None the defaults will be used.
      - If there is only one candidate (or all raw scores equal) the normalized score
        will be 100 for all candidates (by design).
    """
    results: List[Dict[str, Any]] = []

    if not candidates:
        return []

    # Compute component scores and raw score
    for cand in candidates:
        semantic = compute_semantic_score(job_description, cand.get("summary", ""))
        skill = compute_skill_score(required_skills, cand.get("skills", []))
        exp = compute_experience_score(required_experience, cand.get("experience", ""))

        raw = compute_weighted_score(semantic, skill, exp, weights or {})

        results.append({
            "candidate": cand,
            "semantic": semantic,
            "skills": skill,
            "experience": exp,
            "raw_score": raw
        })

    # Normalize raw scores into 0-100
    raw_scores = [r["raw_score"] for r in results]
    min_score = min(raw_scores)
    max_score = max(raw_scores)

    for r in results:
        r["score"] = normalize_score(r["raw_score"], min_score, max_score)

    # Sort by normalized score (desc)
    return sorted(results, key=lambda x: x["score"], reverse=True)


# Example: quick smoke test when run as script
if __name__ == "__main__":
    jd = "Senior Python engineer with AWS and microservices experience"
    skills = ["python", "aws", "microservices"]
    candidates = [
        {"name": "Alice", "summary": "python developer with aws experience", "skills": ["python", "aws"], "experience": "senior"},
        {"name": "Bob", "summary": "java engineer", "skills": ["java"], "experience": "mid"},
    ]
    res = rank_candidates(jd, skills, "senior", candidates, weights=None)
    for r in res:
        print(r["candidate"]["name"], r["score"])
