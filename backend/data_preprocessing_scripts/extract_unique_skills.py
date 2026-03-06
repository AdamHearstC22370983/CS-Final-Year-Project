import pandas as pd
import json
import re
from pathlib import Path
from ast import literal_eval

CSV_PATH = "JobsDatasetProcessed.csv"  # adjust if needed

IT_COL = "IT Skills"
SOFT_COL = "Soft Skills"  # optional

OUT_IT_JSON = "it_skills_library.json"
OUT_IT_TXT = "it_skills_library.txt"

OUT_SOFT_JSON = "soft_skills_library.json"
OUT_SOFT_TXT = "soft_skills_library.txt"


def parse_cell(cell) -> list[str]:
#    Parse a skills cell that might be:
#       - JSON list string: ["python","sql"]
#       - Python list string: ['python', 'sql']
#       - Delimited string: python, sql | docker; kubernetes
#       - Empty/NaN

    if cell is None:
        return []
    s = str(cell).strip()
    if not s or s.lower() in {"nan", "none", "null"}:
        return []

    # Try literal_eval for Python-list-like strings safely
    if s.startswith("[") and s.endswith("]"):
        try:
            val = literal_eval(s)  # handles ['a','b'] and ["a","b"]
            if isinstance(val, list):
                return [str(x) for x in val]
        except Exception:
            pass

        # Try JSON loads
        try:
            val = json.loads(s)
            if isinstance(val, list):
                return [str(x) for x in val]
        except Exception:
            pass

    # Fallback: split on common delimiters
    parts = re.split(r"[|,;/]+", s)
    return [p.strip() for p in parts if p and p.strip()]


def normalise(skill: str) -> str:
    s = (skill or "").strip().lower()
    s = re.sub(r"\s+", " ", s)
    s = s.strip(" .,:;|/\\-–—()[]{}\"'")
    return s


def extract_unique(df: pd.DataFrame, col_name: str) -> list[str]:
    if col_name not in df.columns:
        raise ValueError(f"Column '{col_name}' not found. Columns: {list(df.columns)}")

    unique = set()
    for cell in df[col_name].tolist():
        for raw in parse_cell(cell):
            sk = normalise(raw)
            if sk:
                unique.add(sk)

    return sorted(unique)


def write_outputs(skills: list[str], out_json: str, out_txt: str):
    Path(out_json).write_text(json.dumps(skills, indent=2, ensure_ascii=False), encoding="utf-8")
    Path(out_txt).write_text("\n".join(skills), encoding="utf-8")


def main():
    df = pd.read_csv(CSV_PATH)

    it_skills = extract_unique(df, IT_COL)
    write_outputs(it_skills, OUT_IT_JSON, OUT_IT_TXT)

    print(f"Unique IT skills: {len(it_skills)}")
    print("First 30 IT skills:")
    for s in it_skills[:30]:
        print(" -", s)

    # OPTIONAL: also output soft skills
    if SOFT_COL in df.columns:
        soft_skills = extract_unique(df, SOFT_COL)
        write_outputs(soft_skills, OUT_SOFT_JSON, OUT_SOFT_TXT)
        print(f"\nUnique Soft skills: {len(soft_skills)}")

if __name__ == "__main__":
    main()