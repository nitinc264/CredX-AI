from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import os

# import your ranking logic (file at repo root)
import matching_engine

app = FastAPI(title='CredX Rank API')

# Load sample candidates by default
CAND_PATH = os.path.join(os.path.dirname(__file__), 'data', 'candidates.json')
try:
    with open(CAND_PATH, 'r', encoding='utf-8') as f:
        DEFAULT_CANDIDATES = json.load(f)
except Exception:
    DEFAULT_CANDIDATES = []

class RankRequest(BaseModel):
    text: Optional[str] = ""
    user_prefs: Optional[Dict[str, float]] = {}
    required_skills: Optional[List[str]] = []
    required_experience: Optional[str] = ""
    weights: Optional[Dict[str, float]] = None
    candidates: Optional[List[Dict[str, Any]]] = None
    top_k: Optional[int] = 10

@app.post('/rank')
def rank(req: RankRequest):
    try:
        candidates = req.candidates if req.candidates is not None else DEFAULT_CANDIDATES
        # Ensure weights come from config if not provided
        if req.weights:
            weights = req.weights
        else:
            cfg_path = os.path.join(os.path.dirname(__file__), 'config', 'ranking_weights.json')
            try:
                with open(cfg_path, 'r', encoding='utf-8') as f:
                    cfg = json.load(f)
                    weights = cfg.get('weights', {})
            except Exception:
                weights = {"semantic": 0.4, "preference": 0.0, "skill_relevance": 0.4, "experience": 0.2}

        results = matching_engine.rank_candidates(
            job_description=req.text or "",
            required_skills=req.required_skills or [],
            required_experience=req.required_experience or "",
            candidates=candidates,
            weights=weights
        )

        # Respect top_k
        top = results[: req.top_k] if req.top_k else results

        # Return minimal info
        return {"results": [{"id": r["candidate"].get("id"), "score": r["score"], "meta": r["candidate"]} for r in top]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# quick root
@app.get('/')
def root():
    return {"status":"ok", "endpoint":"/rank"}
