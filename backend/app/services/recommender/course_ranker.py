# app/services/recommender/course_ranker.py
# Uses internal similarity scoring for ranking
# Returns user-friendly recommendation output
# Supports guided-question inputs:
#   - experience_level
#   - has_taken_course
# Raw scores are not exposed to the user

from __future__ import annotations
from typing import Any, Dict, List, Optional, Set
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session
from app.services.recommender.scoring import jaccard, tfidf_cosine_scores, weighted_final

SYNONYMS = {
    "rest": "rest api",
    "restful api": "rest api",
    "golang": "go",
    "g-rpc": "grpc",
    "g rpc": "grpc",
    "k8s": "kubernetes",
}

LEVEL_MAP = {
    "beginner": {"beginner", "introductory", "foundation", "foundational", "foundations", "basic"},
    "intermediate": {"intermediate"},
    "advanced": {"advanced"},
}


def _norm(s: str) -> str:
    return (s or "").strip().lower()


def _apply_synonyms(values: Set[str]) -> Set[str]:
    return {SYNONYMS.get(v, v) for v in values}


def _to_pg_array_literal(values: Set[str]) -> str:
    return "{" + ",".join(sorted(values)) + "}"


def _infer_level_filter(experience_level: Optional[str], has_taken_course: Optional[bool]) -> Optional[str]:
    if experience_level:
        lv = _norm(experience_level)
        if lv in {"beginner", "intermediate", "advanced"}:
            return lv

    if has_taken_course is False:
        return "beginner"

    return None


def _recommendation_label(coverage: float) -> str:
    if coverage >= 0.50:
        return "Highly recommended"
    if coverage >= 0.25:
        return "Recommended"
    return "Consider"


def _consistent_fields(rows: List[Dict[str, Any]], field: str, threshold: float = 0.80) -> bool:
    if not rows:
        return False
    present = sum(1 for row in rows if row.get(field) is not None)
    return (present / len(rows)) >= threshold


def _get_course_columns(db: Session) -> Set[str]:
    engine = db.get_bind()
    inspector = inspect(engine)
    return {col["name"].lower() for col in inspector.get_columns("courses")}


def rank_courses_for_missing(
    db: Session,
    missing_entities: List[str],
    top_n: int = 10,
    use_cosine: bool = True,
    experience_level: Optional[str] = None,
    has_taken_course: Optional[bool] = None,
    w_jaccard: float = 0.75,
    w_cosine: float = 0.25,
) -> List[Dict[str, Any]]:
    missing = {_norm(str(m)) for m in (missing_entities or []) if str(m).strip()}
    missing = _apply_synonyms(missing)

    if not missing:
        return []

    course_columns = _get_course_columns(db)
    if "skills_norm" not in course_columns:
        return []

    level_filter = _infer_level_filter(experience_level, has_taken_course)
    allowed_levels = LEVEL_MAP.get(level_filter) if level_filter else None

    params: Dict[str, Any] = {"missing": _to_pg_array_literal(missing)}

    base_match_sql = "skills_norm IS NOT NULL AND skills_norm ?| :missing"

    grpc_fallback_sql = ""
    if "grpc" in missing:
        description_col = "description" if "description" in course_columns else "NULL"
        grpc_fallback_sql = (
            " OR lower(course_name) LIKE '%grpc%'"
            f" OR lower(COALESCE({description_col}, '')) LIKE '%grpc%'"
            f" OR lower(COALESCE({description_col}, '')) LIKE '%remote procedure%'"
        )

    level_clause = ""
    if allowed_levels and "level" in course_columns:
        params["levels"] = list(allowed_levels)
        level_clause = " AND level IS NOT NULL AND lower(level) = ANY(:levels)"

    org_expr = "organization"
    if "organization" not in course_columns and "organisation" in course_columns:
        org_expr = "organisation AS organization"
    elif "organization" not in course_columns:
        org_expr = "NULL AS organization"

    optional_columns = {
        "type": "type",
        "level": "level",
        "subject": "subject",
        "duration": "duration",
        "rating": "rating",
        "nu_reviews": "nu_reviews",
        "enrollments": "enrollments",
        "description": "description",
    }

    select_parts = [
        "id",
        "url",
        "course_name",
        "provider",
        org_expr,
    ]
    for alias, col_name in optional_columns.items():
        if col_name in course_columns:
            select_parts.append(col_name)
        else:
            select_parts.append(f"NULL AS {alias}")
    select_parts.append("skills_norm")

    sql = text(f"""
        SELECT
            {', '.join(select_parts)}
        FROM courses
        WHERE ({base_match_sql}{grpc_fallback_sql})
        {level_clause}
        LIMIT 2500
    """)

    rows = db.execute(sql, params).mappings().all()
    if not rows:
        return []

    docs: List[str] = []
    for row in rows:
        name = str(row.get("course_name") or "")
        desc = str(row.get("description") or "")
        docs.append(f"{name}. {desc}")

    query_text = " ".join(sorted(missing))
    cosine_scores = tfidf_cosine_scores(query_text, docs) if use_cosine else [0.0] * len(rows)

    internal_ranked: List[Dict[str, Any]] = []
    missing_count = len(missing)

    for row, cos in zip(rows, cosine_scores):
        skills_norm = [str(x).strip().lower() for x in (row.get("skills_norm") or []) if str(x).strip()]
        matched = sorted(set(skills_norm) & missing)
        matched_count = len(matched)

        if matched_count == 0:
            continue

        jac = jaccard(missing, skills_norm)
        final = weighted_final(jaccard_score=jac, cosine_score=cos, w_j=w_jaccard, w_c=w_cosine)
        coverage = matched_count / missing_count if missing_count > 0 else 0.0

        internal_ranked.append({
            "course_id": row.get("id"),
            "url": row.get("url"),
            "course_name": row.get("course_name"),
            "provider": row.get("provider"),
            "organization": row.get("organization"),
            "type": row.get("type"),
            "level": row.get("level"),
            "subject": row.get("subject"),
            "duration": row.get("duration"),
            "rating": row.get("rating"),
            "nu_reviews": row.get("nu_reviews"),
            "enrollments": row.get("enrollments"),
            "matched_skills": matched,
            "matched_count": matched_count,
            "covers": f"{matched_count}/{missing_count}",
            "recommendation_label": _recommendation_label(coverage),
            "_final": float(final),
            "_coverage": float(coverage),
        })

    internal_ranked.sort(
        key=lambda x: (x["_final"], x["_coverage"], x["matched_count"]),
        reverse=True,
    )

    top = internal_ranked[:top_n]

    include_org = _consistent_fields(top, "organization", threshold=0.80)
    include_level = _consistent_fields(top, "level", threshold=0.80)
    include_type = _consistent_fields(top, "type", threshold=0.80)
    include_subject = _consistent_fields(top, "subject", threshold=0.80)
    include_duration = _consistent_fields(top, "duration", threshold=0.80)
    include_rating = _consistent_fields(top, "rating", threshold=0.80)
    include_reviews = _consistent_fields(top, "nu_reviews", threshold=0.80)
    include_enrollments = _consistent_fields(top, "enrollments", threshold=0.80)

    output: List[Dict[str, Any]] = []
    for row in top:
        item: Dict[str, Any] = {
            "course_id": row["course_id"],
            "url": row["url"],
            "course_name": row["course_name"],
            "provider": row["provider"],
            "recommendation_label": row["recommendation_label"],
            "covers": row["covers"],
            "matched_skills": row["matched_skills"],
            "matched_count": row["matched_count"],
        }
        if include_org:
            item["organization"] = row.get("organization")
        if include_level:
            item["level"] = row.get("level")
        if include_type:
            item["type"] = row.get("type")
        if include_subject:
            item["subject"] = row.get("subject")
        if include_duration:
            item["duration"] = row.get("duration")
        if include_rating:
            item["rating"] = row.get("rating")
        if include_reviews:
            item["nu_reviews"] = row.get("nu_reviews")
        if include_enrollments:
            item["enrollments"] = row.get("enrollments")
        output.append(item)
    return output
