# course_ranker.py
from __future__ import annotations
from typing import Any, Dict, List, Set
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.services.recommender.scoring import jaccard, tfidf_cosine_scores, weighted_final

# Minimal synonym/canonical map to improve matching between missing entities and course skills
# This is important because your gap snapshot might contain "rest" while the catalog uses "rest api"
SYNONYMS = {
    "rest": "rest api",
    "golang": "go",
    "g-rpc": "grpc",
    "g rpc": "grpc",
    "k8s": "kubernetes",
    ".net": "dotnet",
    "postgres": "postgresql" 
}

# Format float as percentage with one decimal place, e.g. 0.091 -> 9.1
def _pct1(x: float) -> float:
    try:
        return round(float(x) * 100.0, 1)
    except Exception:
        return 0.0

# Normalize string to a canonical comparison form
def _norm(s: str) -> str:
    return (s or "").strip().lower()

# Apply synonyms to a set of skills
def _apply_synonyms(skills: Set[str]) -> Set[str]:
    out: Set[str] = set()
    for s in skills:
        out.add(SYNONYMS.get(s, s))
    return out

# Convert a python set into a Postgres array literal for jsonb ?| operator
# Example: {"docker","go","rest api"}
def _to_pg_array_literal(values: Set[str]) -> str:
    # Values should be lowercase and should not include braces
    # Note: if a value contains a comma, this becomes unsafe; for your skill labels this is usually fine
    return "{" + ",".join(sorted(values)) + "}"

def rank_courses_for_missing(
    db: Session,
    missing_entities: List[str],
    top_n: int = 25,
    use_cosine: bool = True,
    w_jaccard: float = 0.75,
    w_cosine: float = 0.25,
) -> List[Dict[str, Any]]:
    # Normalize + canonicalize missing entities
    missing_set = {_norm(str(m)) for m in (missing_entities or []) if str(m).strip()}
    missing_set = _apply_synonyms(missing_set)

    if not missing_set:
        return []

    # Candidate filtering using jsonb ?| operator:
    # This returns only courses where skills_norm contains ANY of the missing terms
    # This prevents random limiting from missing relevant courses (docker/go/rest api/etc)
    sql = text("""
        SELECT
            id, url, course_name, provider, organization, organisation, type, level, subject,
            duration, rating, nu_reviews, enrollments, description, skills_norm
        FROM courses
        WHERE skills_norm IS NOT NULL
          AND skills_norm ?| :missing
        LIMIT 2000
    """)

    missing_pg = _to_pg_array_literal(missing_set)
    rows = db.execute(sql, {"missing": missing_pg}).mappings().all()

    if not rows:
        return []

    # Build TF-IDF docs list for cosine scoring (optional)
    docs: List[str] = []
    for r in rows:
        name = str(r.get("course_name") or "")
        desc = str(r.get("description") or "")
        docs.append(f"{name}. {desc}")
    # The query for cosine similarity is just the missing skills joined together, which is a simple but effective way to get a relevance signal that complements Jaccard.
    query_text = " ".join(sorted(missing_set))
    cosine_scores = tfidf_cosine_scores(query_text, docs) if use_cosine else [0.0] * len(rows)

    scored: List[Dict[str, Any]] = []
    for r, cos in zip(rows, cosine_scores):
        skills_norm = [str(x).strip().lower() for x in (r.get("skills_norm") or []) if str(x).strip()]
        # Core similarity
        jac = jaccard(missing_set, skills_norm)
        # Explainability
        matched = sorted(set(skills_norm) & set(missing_set))
        if not matched:
            # If it passed SQL filtering but doesn't match after normalization, skip it
            continue

        # Final blended score
        final = weighted_final(jaccard_score=jac, cosine_score=cos, w_j=w_jaccard, w_c=w_cosine)

        scored.append({
            "course_id": r.get("id"),
            "url": r.get("url"),
            "course_name": r.get("course_name"),
            "provider": r.get("provider"),
            # Handle both spellings just in case your DB uses one or the other
            "organization": r.get("organization") or r.get("organisation"),
            "type": r.get("type"),
            "level": r.get("level"),
            "subject": r.get("subject"),
            "duration": r.get("duration"),
            "rating": r.get("rating"),
            "nu_reviews": r.get("nu_reviews"),
            "enrollments": r.get("enrollments"),
            "skills_norm": skills_norm,
            # Clean UI-ready score formatting
            "score_jaccard_pct": _pct1(jac),
            "score_cosine_pct": _pct1(float(cos)),
            "final_score_pct": _pct1(final),
            "matched_skills": matched,
            "matched_count": len(matched),
        })
    # Sort by final score then matched_count
    scored.sort(key=lambda x: (x["final_score_pct"], x["matched_count"]), reverse=True)
    return scored[:top_n]
