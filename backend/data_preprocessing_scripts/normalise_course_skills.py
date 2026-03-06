# normalise_course_skills.py
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, List, Set, Dict

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.db import SessionLocal
from app.services.ESCO.esco_normaliser import normalise_entity

# --- Settings ---
BATCH_COMMIT = 50

# If True, any skill not found in taxonomy_map will be sent to ESCO (slower, can introduce weird matches).
# For your "limit as much as possible" goal, keep this False.
FALLBACK_TO_ESCO = False
# If True, will attempt to normalise all skills, even those that already have a non-empty skills_norm.
TAX_MAP_PATH = Path("app/data/skill_taxonomy_map.json")

#--- End of settings ---
def _as_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x) for x in value]
    if isinstance(value, str):
        s = value.strip()
        if not s or s.lower() in {"nan", "none", "null"}:
            return []
        try:
            parsed = json.loads(s)
            if isinstance(parsed, list):
                return [str(x) for x in parsed]
        except Exception:
            return [s]
    return []


def _clean_key(s: str) -> str:
#    Normalises a raw skill string into a key similar to what your taxonomy builder used.
#    Keep it conservative: lowercase + whitespace collapse + trim punctuation.
    t = (s or "").strip().lower()
    t = re.sub(r"\s+", " ", t)
    t = t.strip(" .,:;|/\\-–—()[]{}\"'")
    return t


def _load_tax_map() -> Dict[str, Any]:
    if not TAX_MAP_PATH.exists():
        raise FileNotFoundError(
            f"Missing {TAX_MAP_PATH.resolve()}. "
            "Make sure you generated skill_taxonomy_map.json."
        )
    return json.loads(TAX_MAP_PATH.read_text(encoding="utf-8"))


def normalise_skill_list(raw_skills: List[str], tax_map: Dict[str, Any]) -> List[str]:
    canonical: Set[str] = set()

    for s in raw_skills or []:
        term = str(s).strip()
        if not term:
            continue

        key = _clean_key(term)
        if not key:
            continue

        # 1) Use taxonomy map (fast + ICT-filtered)
        mapped = tax_map.get(key) or tax_map.get(term)  # sometimes raw stored without cleaning
        if mapped and isinstance(mapped, dict):
            label = (mapped.get("preferred_label") or "").strip()
            if label:
                canonical.add(label.lower())
            continue

        # 2) Optional ESCO fallback (slower, may produce odd matches)
        if FALLBACK_TO_ESCO:
            norm = normalise_entity(term)
            label = (norm.get("normalised") or "").strip()
            if label:
                canonical.add(label.lower())

    return sorted(canonical)


def main():
    tax_map = _load_tax_map()

    db: Session = SessionLocal()
    try:
        rows = db.execute(text("SELECT id, skills, skills_norm FROM courses")).fetchall()
        print(f"Courses found: {len(rows)}")

        updated = 0
        processed = 0

        for row in rows:
            course_id = row.id
            raw_skills = _as_list(row.skills)

            # Skip if already normalised and non-empty
            existing_norm = _as_list(row.skills_norm)
            if existing_norm:
                processed += 1
                continue

            new_norm = normalise_skill_list(raw_skills, tax_map)

            db.execute(
                text("UPDATE courses SET skills_norm = :skills_norm WHERE id = :id"),
                {"skills_norm": json.dumps(new_norm), "id": course_id},
            )

            updated += 1
            processed += 1

            if processed % BATCH_COMMIT == 0:
                db.commit()
                print(f"Processed {processed}/{len(rows)} | updated {updated}")

        db.commit()
        print(f"DONE. Processed: {processed} | Updated: {updated}")
        print(f"FALLBACK_TO_ESCO={FALLBACK_TO_ESCO} (taxonomy-map-first mode)")

    finally:
        db.close()


if __name__ == "__main__":
    main()
