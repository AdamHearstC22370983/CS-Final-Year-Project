# esco_normaliser.py
from __future__ import annotations

import re
from typing import Optional, Dict, Any

from app.services.ESCO.esco_client import esco_search_skill

# Manual overrides for ambiguous technical terms (ESCO sometimes misses these or returns odd mappings)
MANUAL_OVERRIDES = {
    "rust": {"preferred_label": "Rust", "concept_uri": None},
    "go": {"preferred_label": "Go", "concept_uri": None},
    "excel": {"preferred_label": "Excel", "concept_uri": None},
    "rest": {"preferred_label": "REST API", "concept_uri": None},
    "stacks": {"preferred_label": "technology stacks", "concept_uri": None},
    "leadership": {"preferred_label": "leadership", "concept_uri": None},
}

# --- Cleaning rules for taxonomy/library minimisation ---
_BAD_PREFIXES = (
    "ability to ",
    "knowledge of ",
    "understanding of ",
    "experience with ",
    "experience in ",
    "strong ",
    "good ",
)

_BAD_EXACT = {
    "&", "and", "a", "an", "the", "etc", "****",
}

# If a cleaned phrase is super long and not obviously IT-related, drop it.
_IT_HINTS = [
    "sql", "python", "java", "javascript", "typescript", "aws", "azure", "gcp",
    "linux", "windows", "docker", "kubernetes", "terraform", "git", "ci/cd",
    "network", "security", "firewall", "cloud", "devops", "api", "rest",
    "postgres", "mysql", "mongodb", "redis", "cisco", "routing", "switching",
    "virtualization", "vmware", "hyper-v", "ansible", "cybersecurity", 
    "penetration testing", "vulnerability assessment", "compliance", "iso27001", 
    "nmap", "wireshark", "splunk", "elk", "security information and event management", "siem"
]


def _clean_for_taxonomy(raw: str) -> Optional[str]:
# Aggressive cleaner used to build taxonomy/library
    if not raw:
        return None
    s = str(raw).strip().lower()
    if not s or s in {"nan", "none", "null"}:
        return None
    if s in _BAD_EXACT:
        return None

    # strip common fluff prefixes
    for p in _BAD_PREFIXES:
        if s.startswith(p):
            s = s[len(p):].strip()

    # remove trailing "(e.g..." fragments
    s = re.sub(r"\(e\.g.*$", "", s).strip()

    # clean punctuation + collapse whitespace
    s = re.sub(r"\s+", " ", s)
    s = s.strip(" .,:;|/\\-–—()[]{}\"'")

    if len(s) < 2:
        return None

    # drop overly long phrases unless they contain IT hints
    if len(s.split()) > 6:
        if not any(h in s for h in _IT_HINTS):
            return None

    return s

def normalise_entity(original_entity: str) -> Dict[str, Any]:
# normalises an entity into a dict with keys via ESCO
    clean = (original_entity or "").strip().lower()
    # Manual overrides first
    if clean in MANUAL_OVERRIDES:
        fix = MANUAL_OVERRIDES[clean]
        return {
            "original": original_entity,
            "normalised": fix["preferred_label"],
            "uri": fix["concept_uri"],
            "source": "MANUAL",
            "type": "skill"
        }

    # Normalise the entity to the ESCO skills and competencies taxonomy
    result = esco_search_skill(clean)
    if result and result.get("preferred_label"):
        return {
            "original": original_entity,
            "normalised": result["preferred_label"],
            "uri": result.get("concept_uri"),
            "source": "ESCO",
            "type": "skill"
        }

    # Fallback on RAW data if it cannot be normalised to a known ICT skill
    return {
        "original": original_entity,
        "normalised": original_entity,
        "uri": None,
        "source": "RAW",
        "type": "unknown"
    }

def normalise_for_taxonomy(raw_skill: str) -> Optional[Dict[str, Any]]:
# Normalises a raw skill string to a cleaned version and ESCO mapping if possible.
    cleaned = _clean_for_taxonomy(raw_skill)
    if not cleaned:
        return None

    # Manual override first
    if cleaned in MANUAL_OVERRIDES:
        fix = MANUAL_OVERRIDES[cleaned]
        return {
            "raw": raw_skill,
            "cleaned": cleaned,
            "preferred_label": fix["preferred_label"],
            "uri": fix["concept_uri"],
            "source": "MANUAL"
        }

    # ESCO lookup (ICT-filtered, cached)
    result = esco_search_skill(cleaned)
    if result and result.get("preferred_label"):
        return {
            "raw": raw_skill,
            "cleaned": cleaned,
            "preferred_label": result["preferred_label"],
            "uri": result.get("concept_uri"),
            "source": "ESCO"
        }
    # Drop if it doesn't map to ICT ESCO skills
    return None