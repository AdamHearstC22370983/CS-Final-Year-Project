# esco_client.py
from __future__ import annotations

import json
from pathlib import Path
from threading import Lock
from typing import Optional, Dict, Any

import requests

# ESCO API client for skill search
# Connects to the official ESCO API and retrieves ICT-only skills.
ESCO_API_BASE = "https://ec.europa.eu/esco/api"

# Restrict ESCO results to ICT-only groups:
# 94  - Software development
# 158 - Computer use (general ICT)
# 157 - Database management
# 51  - Web development
# 265 - Cloud / DevOps
# 123 - AI & Data Science
# 262 - Cybersecurity
# 160 - Data management
# 159 - Networking
# 161 - ICT operations
# 162 - ICT maintenance
# 163 - ICT infrastructure
# 164 - ICT project management
# 125 - Robotics
# 126 - Automation
# 266 - IoT
# 285 - GIS / Geospatial
# 356 - Mapping/Cartography
# 261 - Information Governance
ICT_GROUPS = ",".join([
    "94", "158", "157", "51", "265", "123", "262",
    "160", "159", "161", "162", "163", "164",
    "125", "126", "266", "285", "356", "261"
])

# Disk cache so we don't hammer ESCO when normalising large libraries
# Stored at: app/data/esco_cache.json
_CACHE_PATH = Path(__file__).resolve().parents[2] / "data" / "esco_cache.json"
_CACHE_LOCK = Lock()

# Reuse connections (faster + nicer to ESCO)
_SESSION = requests.Session()

# loads a cache dict from disk
def _load_cache() -> Dict[str, Any]:
    if not _CACHE_PATH.exists():
        return {}
    try:
        return json.loads(_CACHE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}

# Cache is a simple JSON file mapping lowercased query -> result dict or None.
def _save_cache(cache: Dict[str, Any]) -> None:
    _CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _CACHE_PATH.write_text(
        json.dumps(cache, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def esco_search_skill(query: str) -> Optional[Dict[str, str]]:
#    Queries ESCO for ICT-domain skills only.
#    Returns: {"preferred_label": <string>, "concept_uri": <string>}  OR  None
#      - Uses a local JSON cache to avoid repeated network calls.
#      - Cache stores both hits and misses (None) keyed by lowercased query.

    q = (query or "").strip().lower()
    if not q:
        return None

    # cache check
    with _CACHE_LOCK:
        cache = _load_cache()
        if q in cache:
            return cache[q]  # may be None or dict

    # request (use params so query is correctly URL-encoded)
    url = f"{ESCO_API_BASE}/search"
    params = {
        "text": q,
        "type": "skill",
        "language": "en",
        "skillGroupIds": ICT_GROUPS
    }
    # try-except to handle network issues, timeouts, or unexpected responses gracefully.
    try:
        response = _SESSION.get(url, params=params, timeout=10)
    except Exception:
        result = None
    else:
        if response.status_code != 200:
            result = None
        else:
            try:
                data = response.json()
            except Exception:
                data = {}

            results = data.get("_embedded", {}).get("results", [])
            if not results:
                result = None
            else:
                first = results[0]
                preferred = (
                    first.get("preferredLabel", {}).get("en-us")
                    or first.get("preferredLabel", {}).get("en")
                )
                if not preferred:
                    result = None
                else:
                    result = {
                        "preferred_label": preferred,
                        "concept_uri": first.get("uri", "") or ""
                    }

    # Store in cache (including None)
    with _CACHE_LOCK:
        cache = _load_cache()
        cache[q] = result
        _save_cache(cache)

    return result