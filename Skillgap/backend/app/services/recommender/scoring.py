# app/services/recommender/scoring.py
from __future__ import annotations
from typing import Iterable, List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Scoring functions for recommender system. These are all simple heuristics that can be computed on the fly.
def jaccard(a: Iterable[str], b: Iterable[str]) -> float:
    sa = {x.strip().lower() for x in (a or []) if str(x).strip()}
    sb = {x.strip().lower() for x in (b or []) if str(x).strip()}
    if not sa and not sb:
        return 0.0
    if not sa:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def coverage(a_required: Iterable[str], b_candidate: Iterable[str]) -> float:
# How much of required set is covered by candidate set.
    sa = {x.strip().lower() for x in (a_required or []) if str(x).strip()}
    sb = {x.strip().lower() for x in (b_candidate or []) if str(x).strip()}
    if not sa:
        return 0.0
    return len(sa & sb) / len(sa)


def tfidf_cosine_scores(query: str, docs: List[str]) -> List[float]:
#    Returns cosine similarity of query vs each doc using TF-IDF.
#    Compute on candidate set only (fast enough for MVP).

    if not query.strip():
        return [0.0] * len(docs)

    # Stop words helps remove junk like "for", "and", "with"
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=50000)

    X = vectorizer.fit_transform([query] + docs)
    q_vec = X[0:1]
    d_vec = X[1:]

    sims = cosine_similarity(q_vec, d_vec).flatten()
    return [float(x) for x in sims]


def weighted_final(jaccard_score: float, cosine_score: float, w_j: float = 0.75, w_c: float = 0.25) -> float:
#   Simple weighted blend. For initial system, heavily weight Jaccard.
#   Clamp
    j = max(0.0, min(1.0, jaccard_score))
    c = max(0.0, min(1.0, cosine_score))
    return (w_j * j) + (w_c * c)