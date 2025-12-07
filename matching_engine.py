import re
import math
from typing import List, Dict, Any


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
    """
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
    If either level is missing or unknown, returns 0.0.
    """
    if not required or not candidate:
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
    Default weights used if missing or zero.
    Returns a raw score in [0.0, 1.0] (assuming inputs are in [0,1]).
    """
    # defaults
    w_sem = weights.get("semantic", 0.4)
    w_skill = weights.get("skill_relevance", 0.3)
    w_exp = weights.get("experience", 0.3)

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
