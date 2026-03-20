from __future__ import annotations

import json
from pathlib import Path
from typing import Any, List, Set

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.db import SessionLocal

ACTIVE_TAX_PATH = Path("app/data/skill_taxonomy_it_active.json")
BATCH_COMMIT = 100


def _as_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x) for x in value]
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return []
        try:
            parsed = json.loads(s)
            if isinstance(parsed, list):
                return [str(x) for x in parsed]
        except Exception:
            return []
    return []


def norm(s: str) -> str:
    return (s or "").strip().lower()


def main():
    if not ACTIVE_TAX_PATH.exists():
        raise FileNotFoundError(f"Missing {ACTIVE_TAX_PATH.resolve()}")

    active = json.loads(ACTIVE_TAX_PATH.read_text(encoding="utf-8"))
    active_set: Set[str] = {norm(x) for x in active if norm(str(x))}
    print(f"Active taxonomy loaded: {len(active_set)} skills")

    db: Session = SessionLocal()
    try:
        rows = db.execute(text("SELECT id, skills_norm FROM courses WHERE skills_norm IS NOT NULL")).fetchall()
        print(f"Courses with skills_norm: {len(rows)}")

        updated = 0
        for i, row in enumerate(rows, start=1):
            course_id = row.id
            current = [norm(x) for x in _as_list(row.skills_norm) if norm(x)]
            cleaned = sorted(set(current).intersection(active_set))

            if set(cleaned) != set(current):
                db.execute(
                    text("UPDATE courses SET skills_norm = :skills_norm WHERE id = :id"),
                    {"skills_norm": json.dumps(cleaned), "id": course_id},
                )
                updated += 1

            if i % BATCH_COMMIT == 0:
                db.commit()
                print(f"Processed {i}/{len(rows)} | updated {updated}")

        db.commit()
        print(f"DONE. Updated courses: {updated}")

    finally:
        db.close()

if __name__ == "__main__":
    main()