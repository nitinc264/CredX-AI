# NEW
from .semantic_matcher import SemanticMatcher

class SkillsScorer:
    def __init__(self):
        self.semantic_matcher = SemanticMatcher()

    def _calculate_jaccard_similarity(self, set1, set2):
        if not set1 and not set2:
            return 1.0
        if not set1 or not set2:
            return 0.0
            
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union if union != 0 else 0.0

    def calculate_score(self, candidate_skills, job_skills):
        if not job_skills:
            return 0

        exact_match_score = self._calculate_jaccard_similarity(set(candidate_skills), set(job_skills))
        
        semantic_competency_score = self.semantic_matcher.get_similarity(candidate_skills, job_skills)
        
        competency_score = (0.4 * exact_match_score + 0.6 * semantic_competency_score) if candidate_skills else 0.0

        return min(competency_score * 100, 100)
