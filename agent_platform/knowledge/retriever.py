import os, json, joblib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

ROOT = os.path.dirname(os.path.dirname(__file__))
INDEX_PATH = os.path.join(ROOT, "knowledge/tfidf_index.pkl")
CHUNK_PATH = os.path.join(ROOT, "knowledge/kb_chunks.jsonl")

class TfidfRAG:
    def __init__(self, index_path: str = INDEX_PATH):
        blob = joblib.load(index_path)
        self.pipe = blob["pipeline"]
        self.X = blob["matrix"]
        self.meta = blob["meta"]

    def search(self, query: str, k: int = 3):
        qv = self.pipe.transform([query])
        sims = cosine_similarity(qv, self.X)[0]
        idx = np.argsort(-sims)[:k]
        results = []
        for i in idx:
            m = self.meta[i]
            results.append({
                "title": m["title"],
                "doc_id": m["doc_id"],
                "category": m["category"],
                "effective_date": m["effective_date"],
                "applicable": m["applicable"],
                "text": m["text"],
                "score": float(sims[i])
            })
        return results
