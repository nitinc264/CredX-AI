import pytest

from matching_engine import (
    compute_semantic_score,
    compute_skill_score,
    compute_experience_score,
    compute_weighted_score,
    rank_candidates,
)


def test_semantic_score_basic_overlap():
    jd = "machine learning python pytorch"
    cand = "Experienced engineer in PyTorch and python for ML"
    score = compute_semantic_score(jd, cand)
    assert score > 0.0
    assert pytest.approx(compute_semantic_score("a b c", "a b c"), rel=1e-6) == 1.0


def test_skill_score_full_and_partial():
    req = ["pytorch", "nlp", "python"]
    cand_full = ["pytorch", "nlp", "python", "mlops"]
    cand_partial = ["python", "pandas"]
    assert compute_skill_score(req, cand_full) == 1.0
    assert 0.0 < compute_skill_score(req, cand_partial) < 1.0
    assert compute_skill_score([], cand_full) == 0.0


def test_experience_score_exact_above_below():
    assert compute_experience_score("mid", "senior") == 1.0
    assert compute_experience_score("mid", "mid") == 1.0
    val = compute_experience_score("senior", "junior")
    assert 0.0 <= val < 1.0


def test_weighted_score_combination_behavior():
    weights = {"semantic": 0.4, "skill_relevance": 0.3, "experience": 0.3}
    raw = compute_weighted_score(1.0, 1.0, 1.0, weights)
    assert pytest.approx(raw, rel=1e-6) == sum(weights.values())

    raw2 = compute_weighted_score(0.0, 1.0, 1.0, weights)
    assert raw2 < raw


def test_rank_candidates_ordering_and_normalization():
    jd = "ml engineer with pytorch and nlp"
    req_skills = ["pytorch", "nlp"]
    req_exp = "mid"
    weights = {"semantic": 0.4, "skill_relevance": 0.4, "experience": 0.2}

    candidates = [
        {"id": "c_low", "summary": "junior javascript dev", "skills": ["javascript"], "experience": "junior"},
        {"id": "c_mid", "summary": "mid backend python, some ml", "skills": ["python"], "experience": "mid"},
        {"id": "c_high", "summary": "senior ML engineer with PyTorch and NLP experience", "skills": ["pytorch", "nlp"], "experience": "senior"},
    ]

    results = rank_candidates(jd, req_skills, req_exp, candidates, weights)

    assert results[0]["candidate"]["id"] == "c_high"

    for r in results:
        assert 0.0 <= r["score"] <= 100.0

    raw_scores = [r["raw_score"] for r in results]
    scores = [r["score"] for r in results]
    assert raw_scores.index(max(raw_scores)) == scores.index(max(scores))


def test_edge_cases_empty_candidates():
    res = rank_candidates("a", [], "junior", [], {"semantic": 0.4, "skill_relevance": 0.3, "experience": 0.3})
    assert res == []
