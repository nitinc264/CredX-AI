# file: semantic_matcher.py

from sentence_transformers import SentenceTransformer, util
import torch

class SemanticMatcher:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SemanticMatcher, cls).__new__(cls)
            try:
                cls._model = SentenceTransformer('all-MiniLM-L6-v2')
                print("Semantic model loaded successfully.")
            except Exception as e:
                print(f"Error loading sentence-transformer model: {e}")
                cls._model = None
        return cls._instance

    def get_similarity(self, text1, text2):
        if not self._model or not text1 or not text2:
            return 0.0
            
        try:
            embedding1 = self._model.encode(text1, convert_to_tensor=True)
            embedding2 = self._model.encode(text2, convert_to_tensor=True)
            
            cosine_scores = util.cos_sim(embedding1, embedding2)
            
            if isinstance(text1, list):
                if len(text1) == 0:
                    return 0.0
                max_scores = torch.max(cosine_scores, dim=1).values
                return torch.mean(max_scores).item()
            else:
                return cosine_scores[0][0].item()

        except Exception as e:
            print(f"Error calculating similarity: {e}")
            return 0.0
