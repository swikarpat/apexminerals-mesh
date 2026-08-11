import numpy as np
from sentence_transformers import SentenceTransformer
from typing import Optional, Dict, List

class SemanticCache:
    def __init__(self, similarity_threshold: float = 0.95):
        # Downloads a tiny, ultra-fast embedding model locally on first run
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.threshold = similarity_threshold
        self.cache: List[Dict] = []

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        dot_product = np.dot(vec1, vec2)
        norm = np.linalg.norm(vec1) * np.linalg.norm(vec2)
        return float(dot_product / norm) if norm != 0 else 0.0

    def check_cache(self, query: str) -> Optional[str]:
        """Checks if a semantically identical query was recently processed."""
        if not self.cache:
            return None
            
        query_embedding = self.encoder.encode(query)
        
        for entry in self.cache:
            sim = self._cosine_similarity(query_embedding, entry["embedding"])
            if sim >= self.threshold:
                return entry["response"]
                
        return None

    def add_to_cache(self, query: str, response: str):
        """Saves a new query and its response to the vector cache."""
        embedding = self.encoder.encode(query)
        self.cache.append({
            "query": query,
            "embedding": embedding,
            "response": response
        })