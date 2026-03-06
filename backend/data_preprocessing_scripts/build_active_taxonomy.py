# build_active_taxonomy.py
from __future__ import annotations

import json
from pathlib import Path
from typing import Set, Any, List

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.db import SessionLocal

TAXONOMY_FULL = Path("app/data/skill_taxonomy_it.json")
OUT_ACTIVE = Path("app/data/skill_taxonomy_it_active.json")
OUT_STATS = Path("app/data/skill_taxonomy_it_active_stats.json")

# Keep these even if ESCO taxonomy list doesn't include them exactly
MANUAL_KEEP = {
    "rest api",
    "excel",
    "go",
    "rust",
}

def norm(s: str) -> str:
    return (s or "").strip().lower()

def save_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")

def load_full_taxonomy() -> Set[str]:
    skills = json.loads(TAXONOMY_FULL.read_text(encoding="utf-8"))
    return {norm(str(x)) for x in skills if norm(str(x))}

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

def get_course_norm_skills(db: Session) -> Set[str]:
    rows = db.execute(text("SELECT skills_norm FROM courses")).fetchall()
    found: Set[str] = set()
    for row in rows:
        for s in _as_list(row.skills_norm):
            ns = norm(str(s))
            if ns:
                found.add(ns)
    return found

def main():
    db: Session = SessionLocal()
    try:
        full_tax = load_full_taxonomy()
        course_norm = get_course_norm_skills(db)

        active_esco = full_tax.intersection(course_norm)
        active = sorted(set(active_esco).union(MANUAL_KEEP).intersection(course_norm.union(MANUAL_KEEP)))

        save_json(OUT_ACTIVE, active)
        save_json(OUT_STATS, {
            "full_taxonomy_count": len(full_tax),
            "course_norm_skill_count": len(course_norm),
            "active_taxonomy_count": len(active),
            "manual_kept_count": len(MANUAL_KEEP),
        })

        print("=== ACTIVE TAXONOMY BUILT (skills_norm + manual keep) ===")
        print(f"Full taxonomy:        {len(full_tax)}")
        print(f"Course norm skills:   {len(course_norm)}")
        print(f"Active taxonomy:      {len(active)}")
        print(f"Saved: {OUT_ACTIVE.resolve()}")
        print(f"Saved: {OUT_STATS.resolve()}")

    finally:
        db.close()

if __name__ == "__main__":
    main()