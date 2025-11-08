import json, re, os, hashlib, joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import Normalizer

ROOT = os.path.dirname(os.path.dirname(__file__))
KB_PATH = os.path.join(ROOT, "agent_platform/knowledge/hr_kb.json")
CHUNK_PATH = os.path.join(ROOT, "agent_platform/knowledge/kb_chunks.jsonl")
INDEX_PATH = os.path.join(ROOT, "agent_platform/knowledge/tfidf_index.pkl")

def clean(t: str) -> str:
    return re.sub(r"\s+", " ", t).strip()

def make_chunks(entry):
    base = f"{entry['title']}。适用对象：{entry['applicable']}。生效日期：{entry['effective_date']}。{entry['content']}"
    text = clean(base)
    # 简单句段切片
    parts = re.split(r"[。！？]\s*", text)
    chunks = []
    for i, p in enumerate(parts):
        if not p: continue
        chunk = {
            "doc_id": entry["id"],
            "title": entry["title"],
            "category": entry["category"],
            "applicable": entry["applicable"],
            "effective_date": entry["effective_date"],
            "text": p
        }
        chunks.append(chunk)
    return chunks

def main():
    with open(KB_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_chunks = []
    for e in data:
        all_chunks.extend(make_chunks(e))

    with open(CHUNK_PATH, "w", encoding="utf-8") as f:
        for c in all_chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    corpus = [c["text"] for c in all_chunks]
    # 管道 标准 TF-IDF L2 归一
    pipe = Pipeline([
        ("tfidf", TfidfVectorizer(max_features=20000, ngram_range=(1,2))),
        ("norm", Normalizer(copy=False))
    ])
    X = pipe.fit_transform(corpus)

    joblib.dump({
        "pipeline": pipe,
        "matrix": X,
        "meta": all_chunks
    }, INDEX_PATH)

    print(f"OK chunks={len(all_chunks)}  index={INDEX_PATH}")

if __name__ == "__main__":
    main()
