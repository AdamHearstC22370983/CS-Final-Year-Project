# scripts/merge_active_taxonomy.py
# Merges your existing active taxonomy JSON with a second JSON list
# Produces a de-duplicated merged taxonomy JSON (case-insensitive)
# Keeps a stable sorted output for clean diffs in Git

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import List, Set

# Input 1: your current active taxonomy
ACTIVE_PATH = Path("app/data/skill_taxonomy_it_active.json")

# Input 2: the JSON list you pasted (save it as this file)
# Put the JSON you copied from chat into: scripts/active_taxonomy_additions.json
ADDITIONS_PATH = Path("active_taxonomy_additions.json")

# Output: merged taxonomy
OUT_PATH = Path("app/data/skill_taxonomy_it_active_merged.json")

def norm(s: str) -> str:
    # Lowercase, collapse whitespace, trim punctuation
    t = (s or "").strip().lower()
    t = re.sub(r"\s+", " ", t)
    t = t.strip(" .,:;|/\\-–—()[]{}\"'")
    return t

def load_list(path: Path) -> List[str]:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path.resolve()}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"Expected a JSON list in {path}, got {type(data)}")
    return [str(x) for x in data]

def main():
    active_raw = load_list(ACTIVE_PATH)
    add_raw = load_list(ADDITIONS_PATH)

    # De-duplicate case-insensitively while keeping one representative string (normalized)
    merged_set: Set[str] = set()

    for x in active_raw:
        nx = norm(x)
        if nx:
            merged_set.add(nx)

    for x in add_raw:
        nx = norm(x)
        if nx:
            merged_set.add(nx)

    merged = sorted(merged_set)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(merged, indent=2, ensure_ascii=False), encoding="utf-8")

    print("=== MERGE COMPLETE ===")
    print(f"Active input:    {len(active_raw)}")
    print(f"Additions input: {len(add_raw)}")
    print(f"Merged unique:   {len(merged)}")
    print(f"Saved to:        {OUT_PATH.resolve()}")

if __name__ == "__main__":
    main()