"""
CampusFix AI — Machine Learning & Similarity Engine
Implements CPU-based semantic similarity with automatic fallback and safety scanning.
"""

import os
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("campusfix.ml")

# 1. Deterministic Emergency Keywords (Life Safety First)
SAFETY_PATTERNS = [
    r"\bspark(s|ing)?\b",
    r"\b(exposed|bare|hanging)\s+wire(s)?\b",
    r"\bwire\s+hanging\b",
    r"\bgas\s+(leak|smell)\b",
    r"\bflood(ing|ed)?\b",
    r"\bsmoke\b",
    r"\b(caught\s+)?fire(s)?\b(?!\s+(extinguisher|blanket|drill))",
    r"\bflame(s)?\b",
    r"\bburning\b",
    r"\bshort\s+circuit\b",
    r"\bceiling\s+collaps\w*\b",
    r"\belectric(al)?\s+shock\b",
    r"\bbroken\s+glass\b",
    r"\bwater\s+(near|on)\s+(electric|socket|board)\b",
]

def scan_safety_hazard(text: str) -> bool:
    """
    Scans text for urgent physical safety hazards.
    Runs instantaneously before any ML computation.
    """
    if not text:
        return False
    lower_text = text.lower()
    for pattern in SAFETY_PATTERNS:
        if re.search(pattern, lower_text):
            return True
    return False


# 2. Model Loader with Lazy Caching & Graceful Fallback
_model_instance = None
_model_load_attempted = False

def get_sentence_transformer():
    """
    Loads all-MiniLM-L6-v2 on CPU.
    Prefers local 'models/all-MiniLM-L6-v2' folder if present for 100% offline support.
    Returns None if the library or weights fail to load, triggering fallback.
    """
    global _model_instance, _model_load_attempted
    if not _model_load_attempted:
        _model_load_attempted = True
        try:
            from sentence_transformers import SentenceTransformer
            local_model_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "models", "all-MiniLM-L6-v2"
            )

            if os.path.isdir(local_model_path):
                logger.info("Loading local offline model from: %s", local_model_path)
                _model_instance = SentenceTransformer(local_model_path)
            else:
                logger.info("Local model folder not found. Loading all-MiniLM-L6-v2 on CPU...")
                _model_instance = SentenceTransformer("all-MiniLM-L6-v2")

            logger.info("SentenceTransformer loaded successfully.")
        except Exception as e:
            logger.warning(
                "Could not load SentenceTransformer (%s). Activating Scikit-Learn TF-IDF fallback.", e
            )
            _model_instance = None
    return _model_instance


# 3. Core Similarity Engine
def compute_similarity(query_text: str, candidate_texts: list[str]) -> list[float]:
    """
    Computes cosine similarity of query_text against a list of candidate_texts.
    Uses MiniLM if available; falls back to TF-IDF; falls back to lexical overlap.
    """
    if not candidate_texts or not query_text.strip():
        return []

    # Clean and clamp text length (prevent memory DoS)
    clean_query = query_text.strip()[:1000]
    clean_candidates = [c.strip()[:1000] for c in candidate_texts]

    model = get_sentence_transformer()

    # PRIMARY: MiniLM Embeddings
    if model is not None:
        try:
            from sentence_transformers import util
            q_emb = model.encode(clean_query, convert_to_tensor=True)
            cand_embs = model.encode(clean_candidates, convert_to_tensor=True)
            scores = util.cos_sim(q_emb, cand_embs)[0].tolist()
            return [float(s) for s in scores]
        except Exception as e:
            logger.warning("MiniLM inference failed (%s). Falling back to TF-IDF.", e)

    # FALLBACK 1: Scikit-Learn TF-IDF Vectorizer
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        corpus = [clean_query] + clean_candidates
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform(corpus)
        sim_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
        return [float(s) for s in sim_matrix[0].tolist()]
    except Exception as e:
        logger.warning("TF-IDF fallback failed (%s). Falling back to word overlap.", e)

    # FALLBACK 2: Lexical Token Overlap (Zero Dependencies)
    stopwords = {"in", "the", "is", "a", "of", "and", "to", "for", "on", "at", "an", "it"}
    q_words = set(re.findall(r"\w+", clean_query.lower())) - stopwords
    scores = []
    for cand in clean_candidates:
        c_words = set(re.findall(r"\w+", cand.lower())) - stopwords
        if not q_words or not c_words:
            scores.append(0.0)
        else:
            # Overlap coefficient against query
            intersection = len(q_words & c_words)
            scores.append(float(intersection / len(q_words)))
    return scores


# 4. Duplicate Matching Helper
def find_candidate_duplicates(new_title: str, new_desc: str, existing_complaints: list[dict], threshold: float = 0.65) -> list[dict]:
    """
    Given a new report and a list of existing complaints dicts,
    returns complaints that meet the similarity threshold, sorted by highest similarity.
    """
    if not existing_complaints:
        return []

    query_combined = f"{new_title}. {new_desc}"
    candidate_texts = [f"{c['title']}. {c['description']}" for c in existing_complaints]

    scores = compute_similarity(query_combined, candidate_texts)

    results = []
    for complaint, score in zip(existing_complaints, scores):
        if score >= threshold:
            results.append({
                "complaint": complaint,
                "similarity": round(score, 3),
                "confidence": "High" if score >= 0.80 else "Potential"
            })

    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results
