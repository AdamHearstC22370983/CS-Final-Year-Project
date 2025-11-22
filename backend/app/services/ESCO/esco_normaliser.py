# esco_normaliser.py
from app.services.ESCO.esco_client import esco_search_skill

# Manual overrides for ambiguous technical terms
MANUAL_OVERRIDES = {
    "rust": {"preferred_label": "Rust", "concept_uri": None},
    "go": {"preferred_label": "Go", "concept_uri": None},
    "excel": {"preferred_label": "Excel", "concept_uri": None},
    "rest": {"preferred_label": "REST API", "concept_uri": None},
    "stacks": {"preferred_label": "technology stacks", "concept_uri": None},
    "leadership": {"preferred_label": "leadership", "concept_uri": None},
}

def normalise_entity(original_entity: str):
# Normalises a raw CV/JD entity using:
# 1. Manual ICT overrides
# 2. ESCO API (filtered to ICT groups)
# 3. Fallback raw value

    # Clean input
    clean = original_entity.strip().lower()

    # Step 1: Manual overrides for known ICT terms
    if clean in MANUAL_OVERRIDES:
        fix = MANUAL_OVERRIDES[clean]
        return {
            "original": original_entity,
            "normalised": fix["preferred_label"],
            "uri": fix["concept_uri"],
            "source": "MANUAL",
            "type": "skill"
        }
    # Step 2: Query ESCO with ICT-only groups
    result = esco_search_skill(clean)

    # If ESCO returns a match, use it
    if result and result.get("preferred_label"):
        return {
            "original": original_entity,
            "normalised": result["preferred_label"],
            "uri": result["concept_uri"],
            "source": "ESCO",
            "type": "skill"
        }
    # Step 3: Fallback raw entity
    return {
        "original": original_entity,
        "normalised": original_entity,
        "uri": None,
        "source": "RAW",
        "type": "unknown"
    }
