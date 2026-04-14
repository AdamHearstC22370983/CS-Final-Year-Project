# entity_extraction.py
from __future__ import annotations
import json
import re
from pathlib import Path
from functools import lru_cache
from typing import Dict, List, Any, Tuple
import spacy
from spacy.matcher import PhraseMatcher

# Taxonomy files
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
ACTIVE_TAXONOMY_PATH = DATA_DIR / "skill_taxonomy_it_active.json"

# PhraseMatcher doesn't need NER/parser
_nlp = spacy.load("en_core_web_sm", disable=["ner", "parser", "tagger", "lemmatizer"])

QUALIFICATION_KEYWORDS = [
    "degree", "bachelor", "diploma", "professional certificate",
    "bsc", "higher diploma",
    "aws certified", "azure certified", "gcp certified",
    "security+", "network+",
    "cisco certified", "oracle certified", "red hat certified",
]

EXPERIENCE_PATTERNS = [
    r"\b[0-9]+ ?\+? years? experience\b",
    r"\b[0-9]+ ?\+? years?\b",
    r"\bexperience with\b",
]

#  entity extraction function
def _preprocess_text(text: str) -> str:
    if not text:
        return ""
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text

# Loads the taxonomy, builds a PhraseMatcher, and extracts entities from text.
def _load_taxonomy_file() -> Tuple[Path, List[str]]:
    if ACTIVE_TAXONOMY_PATH.exists():
        path = ACTIVE_TAXONOMY_PATH

    if not path.exists():
        raise FileNotFoundError(
            f"No taxonomy file found. Expected either:\n"
            f" - {ACTIVE_TAXONOMY_PATH}\n"
            f"Make sure you generated skill_taxonomy_it_active.json (and optionally the active version)."
        )
    skills = json.loads(path.read_text(encoding="utf-8"))
    #lowercase + unique + longest-first helps overlap behaviour ('machine learning' before 'learning')
    cleaned = sorted({str(s).strip().lower() for s in skills if s and str(s).strip()}, key=len, reverse=True)
    return path, cleaned

# Manual overrides for common IT skill synonyms, typos, or unnormalisable variants.
@lru_cache(maxsize=1)
def _get_taxonomy_and_matcher() -> Tuple[Path, List[str], PhraseMatcher]:
#    Cached loader for runtime speed.
#    If you rebuild the active taxonomy and want FastAPI to pick it up,
#    restart the backend (or clear the cache manually).

    path, skills = _load_taxonomy_file()

    matcher = PhraseMatcher(_nlp.vocab, attr="LOWER")
    patterns = [_nlp.make_doc(s) for s in skills]
    matcher.add("ICT_SKILL", patterns)

    return path, skills, matcher

# Extract skills using a simple dictionary lookup via spaCy's PhraseMatcher.
def _extract_dictionary_skills(text: str) -> List[str]:
    cleaned = _preprocess_text(text)
    if not cleaned:
        return []

    _, _, matcher = _get_taxonomy_and_matcher()
    doc = _nlp(cleaned)
    matches = matcher(doc)

    found = set()
    for _, start, end in matches:
        span = doc[start:end].text.strip().lower()
        if span:
            found.add(span)

    return sorted(found)

# Extract some basic non-skill entities using simple keyword and regex matching.
def _extract_other_entities(text: str) -> List[Dict[str, str]]:
    cleaned = _preprocess_text(text)
    entities: List[Dict[str, str]] = []

    for q in QUALIFICATION_KEYWORDS:
        if q in cleaned:
            entities.append({"text": q, "type": "qualification"})

    for pattern in EXPERIENCE_PATTERNS:
        for match in re.findall(pattern, cleaned):
            entities.append({"text": match, "type": "experience"})

    return entities

def extract_entities(text: str) -> Dict[str, Any]:
# Main function to extract entities from job description text.
    taxonomy_path, taxonomy_skills, _ = _get_taxonomy_and_matcher()
    dictionary_skills = _extract_dictionary_skills(text)
    
    raw_entities: List[Dict[str, str]] = [{"text": s, "type": "technical"} for s in dictionary_skills]
    # Add other entity types (qualifications, experience) to the raw entities list.
    raw_entities.extend(_extract_other_entities(text))
    # Deduplicate entities (e.g. if a skill also matches a qualification keyword, we keep both but only once each).
    seen = set()
    unique: List[Dict[str, str]] = []
    for ent in raw_entities:
        key = (ent["text"], ent["type"])
        if key not in seen:
            unique.append(ent)
            seen.add(key)

    return {
        "raw_entities": raw_entities,
        "unique_entities": unique,
        "meta": {
            "taxonomy_file": str(taxonomy_path),
            "taxonomy_skill_count": len(taxonomy_skills),
            "matched_technical_count": len(dictionary_skills),
            "unique_entity_count": len(unique),
        }
    }