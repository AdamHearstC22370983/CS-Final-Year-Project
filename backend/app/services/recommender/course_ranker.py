# app/services/recommender/course_ranker.py
# Uses internal similarity scoring for ranking
# Returns user-friendly recommendation output
# Supports guided-question inputs:
# - experience_level
# - has_taken_course
# Raw scores are not exposed to the API response

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.recommender.scoring import jaccard, tfidf_cosine_scores, weighted_final


# Synonym map to improve matching between extracted missing entities
# and stored course entities/skills.
SYNONYMS = {
    "rest": "rest api",
    "restful api": "rest api",
    "golang": "go",
    "g-rpc": "grpc",
    "g rpc": "grpc",
    "k8s": "kubernetes",
}


# Loose level mapping because provider level labels are not always consistent.
LEVEL_MAP = {
    "beginner": {"beginner", "introductory", "foundation", "foundational", "foundations", "basic"},
    "intermediate": {"intermediate"},
    "advanced": {"advanced"},
}


# Convert a value to lowercase trimmed text for reliable comparisons.
def _norm(value: Any) -> str:
    return str(value or "").strip().lower()


# Apply the synonym map to a set of already-normalised values.
# This helps ensure that equivalent terms are treated as the same skill/entity.
def _apply_synonyms(values: Set[str]) -> Set[str]:
    output: Set[str] = set()

    for value in values:
        output.add(SYNONYMS.get(value, value))

    return output


# Convert a Python set into a PostgreSQL array literal string.
# This is used with the Postgres jsonb ?| operator when checking overlap
# against the skills_norm column.
def _to_pg_array_literal(values: Set[str]) -> str:
    return "{" + ",".join(sorted(values)) + "}"


# Infer the effective level filter based on guided question answers.
# If the user explicitly selects a level, use it.
# If the user says they have not taken a course before, assume beginner.
# Otherwise do not force a level filter.
def _infer_level_filter(
    experience_level: Optional[str],
    has_taken_course: Optional[bool],
) -> Optional[str]:
    if experience_level:
        level = _norm(experience_level)
        if level in {"beginner", "intermediate", "advanced"}:
            return level

    if has_taken_course is False:
        return "beginner"

    return None


# Clean organisation/organization text before sending it to the frontend.
# This handles values that may have been stored with braces or extra quotes,
# for example:
# {LearnQuest}
# {"Google Cloud"}
def _clean_organization(value: Any) -> Optional[str]:
    if value is None:
        return None

    text_value = str(value).strip()

    if not text_value:
        return None

    if text_value.startswith("{") and text_value.endswith("}"):
        text_value = text_value[1:-1].strip()

    text_value = text_value.replace('\\"', '"').strip()
    text_value = text_value.strip('"').strip()
    text_value = text_value.replace('"', "").strip()

    return text_value or None

# Check whether a course genuinely looks like a Go programming course.
# This prevents false positives caused by the word "go" being too short
# and too common in general language.
def _is_strong_go_course(course_name: str, description: str, skills_norm: List[str]) -> bool:
    text_blob = f"{course_name} {description}".lower()

    strong_terms = [
        "golang",
        "go programming",
        "programming in go",
        "go language",
        "go developer",
    ]

    if any(term in text_blob for term in strong_terms):
        return True

    if "golang" in skills_norm:
        return True

    return False


# Apply extra safeguards for ambiguous entities.
# Right now this is mainly used to stop weak Go matches from passing through.
def _filter_ambiguous_matches(
    matched: List[str],
    course_name: str,
    description: str,
    skills_norm: List[str],
) -> List[str]:
    filtered = list(matched)

    if "go" in filtered and not _is_strong_go_course(course_name, description, skills_norm):
        filtered.remove("go")

    return filtered


# Assign a user-friendly label to each recommendation.
# The label is based mainly on:
# 1. how much of the user's missing gap the course covers
# 2. where it appears in the ranked list
# 3. a small quality bonus from rating/reviews
def _recommendation_label(
    matched_count: int,
    missing_count: int,
    rank_index: int,
    rating: Optional[float] = None,
    nu_reviews: Optional[int] = None,
) -> str:
    if missing_count <= 0:
        return "Exploratory"

    coverage_ratio = matched_count / missing_count

    quality_bonus = 0.0
    if rating is not None and rating >= 4.5:
        quality_bonus += 0.03
    if nu_reviews is not None and nu_reviews >= 100:
        quality_bonus += 0.02

    score = coverage_ratio + quality_bonus

    if score >= 0.40 or (coverage_ratio >= 0.28 and rank_index <= 2):
        return "Recommended"

    if score >= 0.25 or (coverage_ratio >= 0.14 and rank_index <= 4):
        return "Good match"

    if score >= 0.12:
        return "Worth exploring"

    return "Exploratory"


# Check whether an optional field is present often enough across the top results
# to justify exposing it in the API response.
# This avoids returning sparse or inconsistent metadata to the frontend.
def _consistent_fields(rows: List[Dict[str, Any]], field: str, threshold: float = 0.80) -> bool:
    if not rows:
        return False

    present = 0

    for row in rows:
        value = row.get(field)
        if value is not None:
            present += 1

    return (present / len(rows)) >= threshold


# Read the live courses table schema and return the set of available column names.
# This makes the ranker more robust if the database is slightly ahead or behind
# the current Python model definition.
def _get_available_course_columns(db: Session) -> Set[str]:
    sql = text(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'courses'
        """
    )

    rows = db.execute(sql).mappings().all()
    return {str(row["column_name"]).strip().lower() for row in rows}


# Build the SELECT field list dynamically based on which columns actually exist
# in the live courses table.
# This prevents crashes caused by querying columns that are not present.
def _build_select_fields(available_columns: Set[str]) -> List[str]:
    preferred_fields = [
        "id",
        "url",
        "course_name",
        "provider",
        "organization",
        "organisation",
        "type",
        "level",
        "subject",
        "duration",
        "rating",
        "nu_reviews",
        "enrollments",
        "description",
        "skills_norm",
    ]

    return [field for field in preferred_fields if field in available_columns]


# Rank courses for the user's missing entities using:
# - overlap filtering in Postgres
# - Jaccard similarity
# - optional TF-IDF cosine similarity
# - guided-question filtering for level
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
    # Normalise and canonicalise the missing entities first.
    missing = {_norm(entity) for entity in (missing_entities or []) if _norm(entity)}
    missing = _apply_synonyms(missing)

    if not missing:
        return []

    # Infer the level filter from the guided-question answers.
    level_filter = _infer_level_filter(experience_level, has_taken_course)
    allowed_levels = LEVEL_MAP.get(level_filter, None) if level_filter else None

    # Read the live DB schema so we only query columns that actually exist.
    available_columns = _get_available_course_columns(db)
    select_fields = _build_select_fields(available_columns)

    # A valid ranker result requires these minimum columns.
    required_fields = {"id", "url", "course_name", "provider", "description", "skills_norm"}
    if not required_fields.issubset(set(select_fields)):
        return []

    params: Dict[str, Any] = {}
    params["missing"] = _to_pg_array_literal(missing)

    # Base candidate filter:
    # keep only courses whose skills_norm overlaps any missing entity.
    base_match_sql = "skills_norm IS NOT NULL AND skills_norm ?| :missing"

    # Extra fallback for gRPC if it appears in text but not in skills_norm.
    grpc_fallback_sql = ""
    if "grpc" in missing:
        grpc_fallback_sql = (
            " OR lower(course_name) LIKE '%grpc%'"
            " OR lower(description) LIKE '%grpc%'"
            " OR lower(description) LIKE '%remote procedure%'"
        )

    # Optional level filter if one was inferred or explicitly provided.
    level_clause = ""
    if allowed_levels and "level" in available_columns:
        params["levels"] = list(allowed_levels)
        level_clause = " AND level IS NOT NULL AND lower(level) = ANY(:levels)"

    select_sql = ",\n            ".join(select_fields)

    sql = text(
        f"""
        SELECT
            {select_sql}
        FROM courses
        WHERE ({base_match_sql}{grpc_fallback_sql})
        {level_clause}
        LIMIT 2500
        """
    )
    rows = db.execute(sql, params).mappings().all()
    if not rows:
        return []

    # Prepare course documents for optional cosine re-ranking.
    docs: List[str] = []
    for row in rows:
        course_name = str(row.get("course_name") or "")
        description = str(row.get("description") or "")
        docs.append(f"{course_name}. {description}")

    # Create a single query document from the missing entities.
    query_text = " ".join(sorted(missing))
    cosine_scores = tfidf_cosine_scores(query_text, docs) if use_cosine else [0.0] * len(rows)

    internal_ranked: List[Dict[str, Any]] = []
    missing_count = len(missing)

    # Calculate the ranking features for each candidate course.
    for row, cosine_score in zip(rows, cosine_scores):
        course_name = str(row.get("course_name") or "")
        description = str(row.get("description") or "")

        # Normalise and canonicalise the stored course entities.
        raw_skills = row.get("skills_norm") or []
        skills_norm = [_norm(skill) for skill in raw_skills if _norm(skill)]
        skills_norm = sorted(_apply_synonyms(set(skills_norm)))

        # Work out which missing entities this course can cover.
        matched = sorted(set(skills_norm) & set(missing))

        # Apply special handling for ambiguous short entities like "go".
        matched = _filter_ambiguous_matches(
            matched=matched,
            course_name=course_name,
            description=description,
            skills_norm=skills_norm,
        )
        matched_count = len(matched)

        if matched_count == 0:
            continue

        # Calculate the similarity scores used for internal ranking.
        jaccard_score = jaccard(missing, skills_norm)
        final_score = weighted_final(
            jaccard_score=jaccard_score,
            cosine_score=cosine_score,
            w_j=w_jaccard,
            w_c=w_cosine,
        )
        # coverage formula
        coverage = matched_count / missing_count if missing_count > 0 else 0.0

        internal_ranked.append(
            {
                "course_id": row.get("id"),
                "url": row.get("url"),
                "course_name": row.get("course_name"),
                "provider": row.get("provider"),
                "organization": _clean_organization(row.get("organization") or row.get("organisation")),
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

                # Internal-only ranking fields.
                "_final": float(final_score),
                "_coverage": float(coverage),
            }
        )

    # Rank internally by the weighted score, then by coverage, then by matched count.
    internal_ranked.sort(
        key=lambda item: (item["_final"], item["_coverage"], item["matched_count"]),
        reverse=True,
    )

    top = internal_ranked[:top_n]

    # Assign the final user-facing recommendation labels after ranking,
    # so rank position can be taken into account.
    for index, row in enumerate(top):
        row["recommendation_label"] = _recommendation_label(
            matched_count=row["matched_count"],
            missing_count=missing_count,
            rank_index=index,
            rating=row.get("rating"),
            nu_reviews=row.get("nu_reviews"),
        )

    # Only expose optional fields if they are consistently available.
    include_org = _consistent_fields(top, "organization", threshold=0.80)
    include_level = _consistent_fields(top, "level", threshold=0.80)
    include_type = _consistent_fields(top, "type", threshold=0.80)
    include_subject = _consistent_fields(top, "subject", threshold=0.80)
    include_duration = _consistent_fields(top, "duration", threshold=0.80)
    include_rating = _consistent_fields(top, "rating", threshold=0.80)
    include_reviews = _consistent_fields(top, "nu_reviews", threshold=0.80)
    include_enrollments = _consistent_fields(top, "enrollments", threshold=0.80)

    output: List[Dict[str, Any]] = []

    # Build the final user-facing response shape.
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
        # includes optional metadata fields only if they are consistently present
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
    # returns a list of recommended courses
    return output
