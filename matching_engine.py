import math
from typing import List, Dict, Any


# Normalize score to 0-100
def normalize_score(score: float, min_score: float, max_score: float) -> float:
    if max_score - min_score == 0:
        return 0
    return ((score - min_score) / (max_score - min_score)) * 100


# Simple semantic score using word overlap
def compute_semantic_score(text1: str, text2: str) -> float:
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    if not words1:
        return 0.0
    overlap = words1.intersection(words2)
    return len(overlap) / len(words1)


# Compute skill relevance score
def compute_skill_score(required: List[str], candidate_skills: List[str]) -> float:
    if not required:
        return 0.0
    required = set(s.lower() for s in required)
    candidate = set(s.lower() for s in candidate_skills)
    matched = required.intersection(candidate)
    return len(matched) / len(required)


# Experience score
EXPERIENCE_LEVELS = {
    "intern": 0,
    "junior": 1,
    "mid": 2,
    "senior": 3,
    "lead": 4,
}


def compute_experience_score(required: str, candidate: str) -> float:
    if not required or not candidate:
        return 0.0
    r = required.lower()
    c = candidate.lower()

    if r not in EXPERIENCE_LEVELS or c not in EXPERIENCE_LEVELS:
        return 0.0

    r_val = EXPERIENCE_LEVELS[r]
    c_val = EXPERIENCE_LEVELS[c]

    if c_val >= r_val:
        return 1.0
    return c_val / r_val


# Weighted score aggregation
def compute_weighted_score(semantic: float, skill: float, exp: float, weights: Dict[str, float]) -> float:
    w_sem = weights.get("semantic", 0.4)
    w_skill = weights.get("skill_relevance", 0.3)
    w_exp = weights.get("experience", 0.3)
    return (semantic * w_sem) + (skill * w_skill) + (exp * w_exp)


# Full ranking
def rank_candidates(job_description: str, required_skills: List[str], required_experience: str,
                    candidates: List[Dict[str, Any]], weights: Dict[str, float]):
    results = []

    # Early return for empty candidate list
    if not candidates:
        return []

    for cand in candidates:
        semantic = compute_semantic_score(job_description, cand.get("summary", ""))
        skill = compute_skill_score(required_skills, cand.get("skills", []))
        exp = compute_experience_score(required_experience, cand.get("experience", ""))

        raw = compute_weighted_score(semantic, skill, exp, weights)

        results.append({
            "candidate": cand,
            "semantic": semantic,
            "skills": skill,
            "experience": exp,
            "raw_score": raw
        })

    raw_scores = [r["raw_score"] for r in results]
    min_score = min(raw_scores)
    max_score = max(raw_scores)

    for r in results:
        r["score"] = normalize_score(r["raw_score"], min_score, max_score)

    return sorted(results, key=lambda x: x["score"], reverse=True)
