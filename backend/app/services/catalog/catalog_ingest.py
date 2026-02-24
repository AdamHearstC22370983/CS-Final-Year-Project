#catalog_ingest.py (single curated dataset)

# The file contains DB-like rows under a "courses" key, e.g.
#  { "courses": [ { "url": "...", "course_name": "...", ... }, ... ] }

# Source note:
# - This dataset was originally compiled from edX + Coursera sources (Coursera portion derived from Kaggle in earlier steps),
#  then cleaned and manually curated to match Skillgap's "IT + Communication soft-skills" umbrella.

# File reference:
# kaggle_courses.json :contentReference[oaicite:4]{index=4}


from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.course import Course

# Parsing helpers
def _to_int(x: Any) -> Optional[int]:
    # Some fields in the export are messy strings that may have been originally numeric, e.g. "1,234" or " 567 "
    if x is None:
        return None
    if isinstance(x, int):
        return x
    s = str(x).strip()
    if not s:
        return None
    s = s.replace(",", "").replace(" ", "")
    try:
        return int(float(s))
    except Exception:
        return None


def _to_float(x: Any) -> Optional[float]:
    # Some numeric fields in the export are messy strings, e.g. "4.5 out of 5" or "1,234" or "2 345"
    if x is None:
        return None
    if isinstance(x, float):
        return x
    s = str(x).strip()
    if not s:
        return None
    s = s.replace(",", "").replace(" ", "")
    try:
        return float(s)
    except Exception:
        return None


def _clean_braced_set_text(x: Any) -> Optional[str]:
# Some fields in the export are messy strings that may have been originally sets or lists, e.g.
#  "{'Computer Science', 'Business & Management'}"
    if x is None:
        return None
    s = str(x).strip()
    if not s:
        return None

    # strip outer braces if present
    if s.startswith("{") and s.endswith("}"):
        s = s[1:-1].strip()

    # remove escaped quotes and normal quotes
    s = s.replace('\\"', '"').strip()
    s = s.strip('"').strip()

    # if it looks like CSV inside, keep as CSV
    # e.g.  "Computer Science","Business & Management"
    s = s.replace('"', "").strip()

    # collapse double spaces
    s = " ".join(s.split())
    return s or None


def _parse_skills_field(skills_raw: Any) -> List[str]:
    # skills is usually a STRING that looks like JSON:
    #  '["SQL", "Python Programming"]'

    # But for many edX rows, it's a stringified list of strings that look like dicts:
      #'["{\'skill\': \'Cloud Computing\', ...}", "{\'skill\': \'AWS\', ...}"]'

    # We output: List[str] of skill names.

    if skills_raw is None:
        return []

    # If already a list (rare)
    if isinstance(skills_raw, list):
        return [str(x).strip() for x in skills_raw if str(x).strip()]

    s = str(skills_raw).strip()
    if not s or s.lower() in {"nan", "none", "null", "[]"}:
        return []

    # Try JSON list parse first
    items: List[Any] = []
    try:
        parsed = json.loads(s)
        if isinstance(parsed, list):
            items = parsed
        elif isinstance(parsed, str):
            items = [parsed]
        else:
            items = [parsed]
    except Exception:
        # Fallback: try Python literal list
        try:
            parsed = ast.literal_eval(s)
            if isinstance(parsed, list):
                items = parsed
            else:
                items = [parsed]
        except Exception:
            # Last resort: treat as single skill blob
            return [s] if s else []

    out: List[str] = []

    for it in items:
        if it is None:
            continue

        # Often items are dict-like strings: "{'skill': 'Cloud Computing', ...}"
        if isinstance(it, str):
            t = it.strip()
            if not t:
                continue

            # If it looks like a dict-as-string, try literal_eval and pick 'skill'
            if t.startswith("{") and "skill" in t:
                try:
                    d = ast.literal_eval(t)
                    if isinstance(d, dict):
                        sk = d.get("skill") or d.get("name")
                        if sk and str(sk).strip():
                            out.append(str(sk).strip())
                            continue
                except Exception:
                    pass

            # Normal string skill
            out.append(t)
            continue

        # Dict directly
        if isinstance(it, dict):
            sk = it.get("skill") or it.get("name")
            if sk and str(sk).strip():
                out.append(str(sk).strip())
            continue

        # Any other type
        out.append(str(it).strip())

    # Deduplicate while preserving order
    seen = set()
    deduped: List[str] = []
    for sk in out:
        if sk and sk not in seen:
            seen.add(sk)
            deduped.append(sk)

    return deduped

def _load_courses_export(path: Path) -> List[Dict[str, Any]]:
#    Expected structure:
#      { "courses": [ { ... }, ... ] }

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict) and isinstance(data.get("courses"), list):
        return data["courses"]

    raise ValueError(f"Unsupported JSON structure in {path}. Expected {{'courses': [...]}}")


# ---------------------------
# Upsert / Replace
# ---------------------------
def upsert_courses(db: Session, rows: List[Dict[str, Any]], batch_size: int = 1000) -> Dict[str, int]:
    # Upsert by URL (Course.url is unique in your schema).

    inserted = 0
    updated = 0
    skipped = 0
    total = len(rows)

    for i in range(0, total, batch_size):
        batch = rows[i : i + batch_size]

        try:
            for r in batch:
                url = (r.get("url") or "").strip()
                name = (r.get("course_name") or "").strip()
                provider = (r.get("provider") or "").strip()

                if not url or not name or not provider:
                    skipped += 1
                    continue

                existing = db.query(Course).filter(Course.url == url).first()

                # Normalize fields from export
                org = _clean_braced_set_text(r.get("organization"))
                subj = _clean_braced_set_text(r.get("subject"))
                skills = _parse_skills_field(r.get("skills"))

                duration = _to_float(r.get("duration"))
                rating = _to_float(r.get("rating"))
                nu_reviews = _to_int(r.get("nu_reviews"))
                enrollments = _to_int(r.get("enrollments"))

                if existing:
                    existing.course_name = name
                    existing.provider = provider
                    existing.organization = org
                    existing.type = r.get("type")
                    existing.level = r.get("level")
                    existing.subject = subj
                    existing.duration = duration
                    existing.rating = rating
                    existing.nu_reviews = nu_reviews
                    existing.enrollments = enrollments
                    existing.description = r.get("description")
                    existing.skills = skills
                    existing.has_rating = _to_int(r.get("has_rating"))
                    existing.has_subject = _to_int(r.get("has_subject"))
                    existing.has_no_enrol = _to_int(r.get("has_no_enrol"))
                    updated += 1
                else:
                    db.add(
                        Course(
                            url=url,
                            course_name=name,
                            provider=provider,
                            organization=org,
                            type=r.get("type"),
                            level=r.get("level"),
                            subject=subj,
                            duration=duration,
                            rating=rating,
                            nu_reviews=nu_reviews,
                            enrollments=enrollments,
                            description=r.get("description"),
                            skills=skills,
                            has_rating=_to_int(r.get("has_rating")),
                            has_subject=_to_int(r.get("has_subject")),
                            has_no_enrol=_to_int(r.get("has_no_enrol")),
                        )
                    )
                    inserted += 1

            db.commit()

        except Exception:
            db.rollback()
            # Fall back to row-by-row for this batch so one bad record doesn't kill import
            for r in batch:
                try:
                    url = (r.get("url") or "").strip()
                    name = (r.get("course_name") or "").strip()
                    provider = (r.get("provider") or "").strip()

                    if not url or not name or not provider:
                        skipped += 1
                        continue

                    existing = db.query(Course).filter(Course.url == url).first()

                    org = _clean_braced_set_text(r.get("organization"))
                    subj = _clean_braced_set_text(r.get("subject"))
                    skills = _parse_skills_field(r.get("skills"))

                    duration = _to_float(r.get("duration"))
                    rating = _to_float(r.get("rating"))
                    nu_reviews = _to_int(r.get("nu_reviews"))
                    enrollments = _to_int(r.get("enrollments"))

                    if existing:
                        existing.course_name = name
                        existing.provider = provider
                        existing.organization = org
                        existing.type = r.get("type")
                        existing.level = r.get("level")
                        existing.subject = subj
                        existing.duration = duration
                        existing.rating = rating
                        existing.nu_reviews = nu_reviews
                        existing.enrollments = enrollments
                        existing.description = r.get("description")
                        existing.skills = skills
                        existing.has_rating = _to_int(r.get("has_rating"))
                        existing.has_subject = _to_int(r.get("has_subject"))
                        existing.has_no_enrol = _to_int(r.get("has_no_enrol"))
                        updated += 1
                    else:
                        db.add(
                            Course(
                                url=url,
                                course_name=name,
                                provider=provider,
                                organization=org,
                                type=r.get("type"),
                                level=r.get("level"),
                                subject=subj,
                                duration=duration,
                                rating=rating,
                                nu_reviews=nu_reviews,
                                enrollments=enrollments,
                                description=r.get("description"),
                                skills=skills,
                                has_rating=_to_int(r.get("has_rating")),
                                has_subject=_to_int(r.get("has_subject")),
                                has_no_enrol=_to_int(r.get("has_no_enrol")),
                            )
                        )
                        inserted += 1

                    db.commit()

                except Exception:
                    db.rollback()
                    skipped += 1

    return {"inserted": inserted, "updated": updated, "skipped": skipped, "total": total}

def ingest_catalog(
    db: Session,
    base_dir: Path,
    filename: str = "kaggle_courses.json",
    truncate_first: bool = True,
) -> Dict[str, int]:
    #Replaces the entire Course catalog from your curated export file.
    # truncate_first=True: wipes Course table then imports
    # truncate_first=False: upserts into existing rows
    
    path = base_dir / filename
    rows = _load_courses_export(path)

    if truncate_first:
        db.query(Course).delete(synchronize_session=False)
        db.commit()

    return upsert_courses(db, rows, batch_size=1000)
