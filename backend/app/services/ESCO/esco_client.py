# esco_client.py
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

# Queries ESCO for ICT-domain skills only.
# Returns: preferred label (string) + concept URI (string)
# Returns None if nothing relevant is found.
def esco_search_skill(query: str):
    # construct request URL
    url = (
        f"{ESCO_API_BASE}/search?"
        f"text={query}&type=skill&language=en&skillGroupIds={ICT_GROUPS}"
    )
    # safe request call
    try:
        response = requests.get(url, timeout=10)
    except Exception:
        return None
    # check response status
    if response.status_code != 200:
        return None
    # parse response
    data = response.json()
    results = data.get("_embedded", {}).get("results", [])

    # no ICT-match found
    if not results:
        return None

    # extract first matching ICT-result
    first = results[0]

    # Correct extraction of English preferred label
    preferred = (
        first.get("preferredLabel", {}).get("en-us")
        or first.get("preferredLabel", {}).get("en")
    )
    if not preferred:
        return None
    # return result
    return {
        "preferred_label": preferred,
        "concept_uri": first.get("uri", "")
    }
