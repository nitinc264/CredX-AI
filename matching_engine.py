# file: matching_engine.py

import pandas as pd
from data_handler import DataHandler
from semantic_matcher import SemanticMatcher
from skills_scorer import SkillsScorer
from story_generator import StoryGenerator
import locale

try:
    locale.setlocale(locale.LC_ALL, 'en_IN')
except locale.Error:
    locale.setlocale(locale.LC_ALL, '')

class Recommender:
    def __init__(self, jobs_file_path, api_key):
        self.data_handler = DataHandler(jobs_file_path)
        self.jobs_df = self.data_handler.get_jobs()
        self.semantic_matcher = SemanticMatcher()
        self.skills_scorer = SkillsScorer()
        self.story_generator = StoryGenerator(api_key=api_key)

    def _get_match_details(self, user_prefs, job_values, is_semantic=False, threshold=0.6):
        details = []
        if not user_prefs:
            return [{'skill': s, 'type': 'none'} for s in job_values]

        norm_user_prefs = {p.lower().strip() for p in user_prefs}

        for job_value in job_values:
            norm_job_value = job_value.lower().strip()
            
            if norm_job_value in norm_user_prefs:
                details.append({'skill': job_value, 'type': 'direct'})
            elif is_semantic:
                similarity = self.semantic_matcher.get_similarity(job_value, user_prefs)
                if similarity > threshold:
                    details.append({'skill': job_value, 'type': 'semantic'})
                else:
                    details.append({'skill': job_value, 'type': 'none'})
            else:
                details.append({'skill': job_value, 'type': 'none'})
        return details

    def get_recommendations(self, preferences):
        if self.jobs_df.empty:
            return []

        candidate_prefs = preferences.get('preferences', {})
        dynamic_weights = preferences.get('weights', {})

        norm_prefs = {
            'titles': {t.lower().strip() for t in candidate_prefs.get('titles', [])},
            'locations': {l.lower().strip() for l in candidate_prefs.get('locations', [])},
            'industries': {i.lower().strip() for i in candidate_prefs.get('industries', [])},
            'employment_types': {e.lower().strip() for e in candidate_prefs.get('employment_types', [])},
        }

        results = []
        for index, job in self.jobs_df.iterrows():
            raw_scores = {
                'skills': self.skills_scorer.calculate_score(
                    candidate_prefs.get('skills', []),
                    job['required_skills']
                ),
                'title': self.semantic_matcher.get_similarity(job['title'], candidate_prefs.get('titles', [])) * 100,
                'location': self._score_list_overlap(norm_prefs['locations'], [job['location'].lower().strip()]),
                'industry': self._score_list_overlap(norm_prefs['industries'], [job['industry'].lower().strip()]),
                'salary': self._score_salary(candidate_prefs.get('min_salary'), job['salary_range']),
                'employment_type': self._score_list_overlap(norm_prefs['employment_types'], [job['employment_type'].lower().strip()])
            }

            if raw_scores['location'] == 0 and norm_prefs['locations']:
                continue

            # Filter by employment type if specified
            if norm_prefs['employment_types'] and raw_scores['employment_type'] == 0:
                continue

            total_weight = sum(dynamic_weights.values())
            if total_weight == 0: continue
            
            final_score = 0
            score_breakdown = {}
            for key, display_name in {
                'skills': 'Skills', 
                'title': 'Title', 
                'location': 'Location', 
                'industry': 'Industry', 
                'salary': 'Salary',
                'employment_type': 'Employment Type'
            }.items():
                contribution = (raw_scores[key] * dynamic_weights.get(key, 0)) / total_weight
                final_score += contribution
                score_breakdown[display_name] = round(contribution)

            rounded_final_score = round(final_score)
            if sum(score_breakdown.values()) != rounded_final_score and score_breakdown:
                max_key = max(score_breakdown, key=score_breakdown.get)
                score_breakdown[max_key] += (rounded_final_score - sum(score_breakdown.values()))

            validation_details = {
                'Skills': self._get_match_details(candidate_prefs.get('skills', []), job['required_skills'], is_semantic=True, threshold=0.5),
                'Title': self._get_match_details(candidate_prefs.get('titles', []), [job['title']], is_semantic=True, threshold=0.6),
                'Location': self._get_match_details(candidate_prefs.get('locations', []), [job['location']]),
                'Industry': self._get_match_details(candidate_prefs.get('industries', []), [job['industry']]),
                'Employment Type': self._get_match_details(candidate_prefs.get('employment_types', []), [job['employment_type']]),
                'Salary': f"₹{locale.format_string('%d', job['salary_range'][0], grouping=True)} - ₹{locale.format_string('%d', job['salary_range'][1], grouping=True)}"
            }

            if final_score > 40:
                results.append({
                    "job_id": job['job_id'],
                    "job_title": job['title'],
                    "company": job['company'],
                    "location": job['location'],
                    "employment_type": job['employment_type'],
                    "match_score": rounded_final_score,
                    "breakdown": score_breakdown,
                    "validation_details": validation_details,
                    "raw_job_details": job.to_dict()
                })

        sorted_results = sorted(results, key=lambda x: x['match_score'], reverse=True)
        
        final_results = []
        for result in sorted_results[:5]: 
            story = self.story_generator.generate_story(
                candidate_prefs=candidate_prefs,
                job_details=result['raw_job_details']
            )
            result['story'] = story
            
            del result['raw_job_details']
            final_results.append(result)

        return final_results

    def _score_salary(self, min_salary_pref, salary_range_job):
        if not min_salary_pref: return 100.0
        return 100.0 if salary_range_job[1] >= min_salary_pref else 0.0
        
    def _score_list_overlap(self, set_pref, list_job_values):
        if not set_pref: return 100.0
        set_job = set(list_job_values)
        intersection = len(set_pref.intersection(set_job))
        union = len(set_pref.union(set_job))
        return (intersection / union) * 100 if union > 0 else 0.0
