# backfill_skills_norm_from_course_text.py
# Backfills courses.skills_norm for rows where skills_norm is NULL or empty
# Extracts skills by phrase matching against your active taxonomy:
#   app/data/skill_taxonomy_it_active.json
# This avoids ESCO calls and improves coverage for terms like docker/kubernetes/grpc/rest api/go/rust

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import List, Set

import spacy
from spacy.matcher import PhraseMatcher
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.db import SessionLocal

ACTIVE_TAX_PATH = Path("app/data/skill_taxonomy_it_active.json")
BATCH_COMMIT = 100

# Phrase matching doesn't need heavy NLP components
nlp = spacy.load("en_core_web_sm", disable=["ner", "parser", "tagger", "lemmatizer"])

def norm(s: str) -> str:
    t = (s or "").strip().lower()
    t = re.sub(r"\s+", " ", t)
    t = t.strip(" .,:;|/\\-–—()[]{}\"'")
    return t

def preprocess(text_in: str) -> str:
    t = (text_in or "").lower()
    t = re.sub(r"\s+", " ", t).strip()
    return t

def load_taxonomy() -> List[str]:
    if not ACTIVE_TAX_PATH.exists():
        raise FileNotFoundError(f"Missing taxonomy file: {ACTIVE_TAX_PATH.resolve()}")

    raw = json.loads(ACTIVE_TAX_PATH.read_text(encoding="utf-8"))
    skills = sorted({norm(str(x)) for x in raw if norm(str(x))}, key=len, reverse=True)
    return skills

def build_matcher(skills: List[str]) -> PhraseMatcher:
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    patterns = [nlp.make_doc(s) for s in skills]
    matcher.add("ICT_SKILL", patterns)
    return matcher

def extract_skills(text_in: str, matcher: PhraseMatcher) -> List[str]:
    t = preprocess(text_in)
    if not t:
        return []

    doc = nlp(t)
    matches = matcher(doc)

    found: Set[str] = set()
    for _, start, end in matches:
        span = doc[start:end].text.strip().lower()
        if span:
            found.add(span)

    return sorted(found)

def main():
    skills = load_taxonomy()
    matcher = build_matcher(skills)

    db: Session = SessionLocal()
    try:
        rows = db.execute(text("""
            SELECT id, course_name, description
            FROM courses
            WHERE skills_norm IS NULL OR jsonb_array_length(skills_norm) = 0
        """)).fetchall()

        print(f"Courses needing backfill: {len(rows)}")
        updated = 0

        for i, row in enumerate(rows, start=1):
            cid = row.id
            name = row.course_name or ""
            desc = row.description or ""

            found = extract_skills(f"{name}. {desc}", matcher)

            db.execute(
                text("UPDATE courses SET skills_norm = :skills_norm WHERE id = :id"),
                {"skills_norm": json.dumps(found), "id": cid},
            )
            updated += 1

            if i % BATCH_COMMIT == 0:
                db.commit()
                print(f"Processed {i}/{len(rows)} | updated {updated}")

        db.commit()
        print(f"DONE. Updated: {updated}")

    finally:
        db.close()

if __name__ == "__main__":
    main()