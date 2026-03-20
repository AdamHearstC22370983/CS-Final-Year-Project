# filter_coursera_ict_batch.py
# Streams processed_coursera_data.json without loading the whole file into memory
# First creates a sanitized temporary copy because the source file contains invalid JSON tokens:
#   NaN, Infinity, -Infinity
# Keeps only ICT-relevant courses using:
#   1) active taxonomy phrase matching
#   2) optional ICT keyword fallback
# Writes output as NDJSON for easy batch ingestion
# Requires: pip install ijson

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, Any, List

import ijson

# Paths kept simple because you moved the script into backend root
IN_PATH = Path("processed_coursera_data.json")
SANITIZED_PATH = Path("processed_coursera_data_sanitized.json")
OUT_NDJSON = Path("processed_coursera_data_ICT.ndjson")
OUT_STATS = Path("processed_coursera_data_ICT_stats.json")
TAXONOMY_PATH = Path("skill_taxonomy_it_active.json")

# Tuning
BATCH_LOG_EVERY = 500
MIN_MATCHES_FROM_TAXONOMY = 1
ALLOW_KEYWORD_FALLBACK = True

# Strong ICT fallback keywords
ICT_KEYWORDS = [
    "software", "programming", "developer", "development", "backend", "back-end", "frontend", "front-end",
    "python", "java", "javascript", "typescript", "sql", "database", "postgres", "mysql", "nosql",
    "cloud", "aws", "azure", "gcp", "docker", "kubernetes", "devops", "ci/cd",
    "api", "rest", "graphql", "grpc", "microservices",
    "cybersecurity", "security", "penetration", "cryptography", "forensics",
    "machine learning", "data science", "artificial intelligence", "ai", "etl", "data engineering", "kafka", "spark",
    "linux", "networking", "tcp/ip", "firewall", "siem", "terraform", "jenkins", "git", "react", "spring"
]

def norm(s: str) -> str:
    t = (s or "").strip().lower()
    t = re.sub(r"\s+", " ", t)
    return t

def load_taxonomy() -> List[str]:
    if not TAXONOMY_PATH.exists():
        raise FileNotFoundError(f"Missing taxonomy file: {TAXONOMY_PATH.resolve()}")

    raw = json.loads(TAXONOMY_PATH.read_text(encoding="utf-8"))
    skills = sorted({norm(str(x)) for x in raw if norm(str(x))}, key=len, reverse=True)
    return skills

def build_patterns(skills: List[str]) -> List[re.Pattern]:
    patterns: List[re.Pattern] = []
    for sk in skills:
        pat = r"(?<!\w)" + re.escape(sk) + r"(?!\w)"
        patterns.append(re.compile(pat, flags=re.IGNORECASE))
    return patterns

def count_taxonomy_matches(text: str, patterns: List[re.Pattern]) -> int:
    t = norm(text)
    if not t:
        return 0

    count = 0
    for rx in patterns:
        if rx.search(t):
            count += 1
            if count >= MIN_MATCHES_FROM_TAXONOMY:
                return count

    return count

def keyword_fallback(text: str) -> bool:
    t = norm(text)
    return any(k in t for k in ICT_KEYWORDS)

def course_text(course: Dict[str, Any]) -> str:
    # Build a searchable blob from common fields
    name = str(course.get("course_name") or course.get("title") or "")
    desc = str(course.get("description") or "")
    org = str(course.get("organization") or "")
    provider = str(course.get("provider") or "")

    skills = course.get("skills") or []
    if isinstance(skills, list):
        skills_txt = " ".join([str(s) for s in skills])
    else:
        skills_txt = str(skills)

    return f"{name}. {desc}. {org}. {provider}. {skills_txt}"

def sanitize_json_file(inp: Path, out: Path) -> None:
    # Replace invalid JSON tokens with null
    # This is safe for this dataset and lets ijson parse it afterward
    print(f"Sanitizing input file: {inp}")
    s = inp.read_text(encoding="utf-8", errors="replace")

    # Replace only bare tokens, not parts of words
    s = re.sub(r"\bNaN\b", "null", s)
    s = re.sub(r"\bInfinity\b", "null", s)
    s = re.sub(r"\b-Infinity\b", "null", s)

    out.write_text(s, encoding="utf-8")
    print(f"Sanitized file written: {out}")

def main():
    print("Starting ICT batch filter...")

    if not IN_PATH.exists():
        raise FileNotFoundError(f"Missing input file: {IN_PATH.resolve()}")

    if not TAXONOMY_PATH.exists():
        raise FileNotFoundError(f"Missing taxonomy file: {TAXONOMY_PATH.resolve()}")

    # Step 1: sanitize invalid JSON tokens
    sanitize_json_file(IN_PATH, SANITIZED_PATH)

    # Step 2: load taxonomy and precompile patterns
    skills = load_taxonomy()
    patterns = build_patterns(skills)

    total = 0
    kept = 0
    dropped = 0

    with open(SANITIZED_PATH, "rb") as f_in, open(OUT_NDJSON, "w", encoding="utf-8") as f_out:
        for course in ijson.items(f_in, "item"):
            total += 1

            text_blob = course_text(course)
            taxonomy_matches = count_taxonomy_matches(text_blob, patterns)

            keep = taxonomy_matches >= MIN_MATCHES_FROM_TAXONOMY

            if not keep and ALLOW_KEYWORD_FALLBACK:
                keep = keyword_fallback(text_blob)

            if keep:
                kept += 1
                f_out.write(json.dumps(course, ensure_ascii=False) + "\n")
            else:
                dropped += 1

            if total % BATCH_LOG_EVERY == 0:
                print(f"Processed: {total} | kept: {kept} | dropped: {dropped}")

    OUT_STATS.write_text(
        json.dumps(
            {
                "input_file": str(IN_PATH),
                "sanitized_file": str(SANITIZED_PATH),
                "output_file": str(OUT_NDJSON),
                "total_processed": total,
                "kept": kept,
                "dropped": dropped,
                "min_taxonomy_matches": MIN_MATCHES_FROM_TAXONOMY,
                "keyword_fallback": ALLOW_KEYWORD_FALLBACK
            },
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    print("DONE")
    print(f"Saved NDJSON: {OUT_NDJSON.resolve()}")
    print(f"Saved stats: {OUT_STATS.resolve()}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("SCRIPT FAILED")
        print(repr(e))
        raise