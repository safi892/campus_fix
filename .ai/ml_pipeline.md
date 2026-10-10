# CampusFix AI — Machine Learning & Deduplication Pipeline

> **AI INSTRUCTION**: ML runs locally on CPU only. Never call external paid APIs. Always wrap ML loading in try/except with TF-IDF fallback. Never let the app crash on model errors.

---

## 1. Multi-Stage Pipeline Overview

```text
Incoming Complaint Text
          │
          ▼
[ Stage 1: Deterministic Safety Scan ] ──(Trigger Match)──► Flag Critical Safety Hazard
          │
          ▼
[ Stage 2: Scope Isolation ] ────────► Filter existing candidates to SAME BUILDING ONLY
          │
          ▼
[ Stage 3: Embedding / Vectorizer ]
     ├── Primary: all-MiniLM-L6-v2 (CPU)
     └── Fallback: Scikit-Learn TF-IDF Vectorizer
          │
          ▼
[ Stage 4: Cosine Similarity Scoring ]
     ├── Score >= 0.80 ──► Suggest Duplicate Cluster
     ├── Score 0.65-0.79 ─► Suggest Possible Related Issue
     └── Score < 0.65  ──► Mark as Distinct Independent Report
          │
          ▼
[ Stage 5: Staff Review & Confirmation ] (Human in the Loop)
```

---

## 2. Stage 1: Deterministic Safety Scanner (Regex)
Runs before vectorization. Zero dependencies, instant speed:

```python
import re

SAFETY_KEYWORDS = [
    r"\bspark(s|ing)?\b",
    r"\bexposed wire(s)?\b",
    r"\bgas (leak|smell)\b",
    r"\bflood(ing|ed)?\b",
    r"\bsmoke\b",
    r"\bfire hazard\b",
    r"\bceiling collaps\w*\b",
    r"\belectric(al)? shock\b",
    r"\bbroken glass\b"
]

def scan_safety_hazard(text: str) -> bool:
    """Returns True if any urgent safety keyword is detected."""
    combined = text.lower()
    for pattern in SAFETY_KEYWORDS:
        if re.search(pattern, combined):
            return True
    return False
```

---

## 3. Stage 2 & 3: Semantic Similarity with Fallback

```python
# ml.py implementation pattern
import numpy as np

_model = None

def get_sentence_transformer():
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as e:
            # Fallback will activate
            _model = False
    return _model

def compute_similarity(new_text: str, candidate_texts: list[str]) -> list[float]:
    """
    Computes cosine similarity of new_text against candidate_texts.
    Falls back seamlessly to TF-IDF if SentenceTransformer is unavailable.
    """
    if not candidate_texts:
        return []

    model = get_sentence_transformer()

    # PRIMARY: SentenceTransformer on CPU
    if model:
        try:
            from sentence_transformers import util
            embeddings_candidates = model.encode(candidate_texts, convert_to_tensor=True)
            embedding_new = model.encode(new_text, convert_to_tensor=True)
            scores = util.cos_sim(embedding_new, embeddings_candidates)[0].tolist()
            return scores
        except Exception:
            pass  # Fall through to TF-IDF

    # FALLBACK: Scikit-Learn TF-IDF + Cosine Similarity
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        
        corpus = [new_text] + candidate_texts
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform(corpus)
        sim_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
        return sim_matrix[0].tolist()
    except Exception:
        # ULTIMATE EMERGENCY FALLBACK: Word token overlap
        words_new = set(new_text.lower().split())
        return [
            len(words_new & set(cand.lower().split())) / max(len(words_new | set(cand.lower().split())), 1)
            for cand in candidate_texts
        ]
```

---

## 4. Duplicate Decision Matrix
* **Scope Constraint**: Candidate comparisons are strictly constrained to complaints where `building == new_complaint.building`.
* **Thresholds**:
  * `score >= 0.80`: **High Confidence Duplicate** $\rightarrow$ Present with `Merge Recommended` badge.
  * `0.65 <= score < 0.80`: **Potential Duplicate** $\rightarrow$ Present for staff visual check.
  * `score < 0.65`: **Independent** $\rightarrow$ No merge suggestion.
