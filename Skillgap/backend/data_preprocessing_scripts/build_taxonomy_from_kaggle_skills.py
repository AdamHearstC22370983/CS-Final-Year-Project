import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.services.ESCO.esco_normaliser import normalise_for_taxonomy


# INPUT
IN_PATH = Path("it_skills_library.json")  # same folder as this script

# OUTPUTS
OUT_DIR = Path("app/data")
OUT_TAXONOMY = OUT_DIR / "skill_taxonomy_it.json"
OUT_MAP = OUT_DIR / "skill_taxonomy_map.json"
OUT_DROPPED = OUT_DIR / "taxonomy_dropped.json"

# RESUME FILE
PROGRESS_PATH = OUT_DIR / "taxonomy_progress.json"

# TUNING
MAX_WORKERS = 6          # try 4–8, not higher
SAVE_EVERY = 100         # progress checkpoint


def load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    raw_skills = load_json(IN_PATH, [])
    if not raw_skills:
        raise ValueError(f"No skills found in {IN_PATH.resolve()}")

    # Load resume data
    progress = load_json(PROGRESS_PATH, {
        "done": [],          # list of raw skill strings processed
        "mapping": {},       # raw -> norm dict
        "dropped": {},       # raw -> reason
    })

    done_set = set(progress.get("done", []))
    mapping = progress.get("mapping", {})
    dropped = progress.get("dropped", {})

    remaining = [s for s in raw_skills if s not in done_set]

    print(f"Total raw skills: {len(raw_skills)}")
    print(f"Already processed (resume): {len(done_set)}")
    print(f"Remaining: {len(remaining)}")
    print(f"Workers: {MAX_WORKERS}")

    processed_since_save = 0

    def worker(raw):
        norm = normalise_for_taxonomy(raw)
        return raw, norm

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(worker, raw): raw for raw in remaining}

        for i, fut in enumerate(as_completed(futures), start=1):
            raw, norm = fut.result()

            # mark as done
            done_set.add(raw)

            if norm is None:
                dropped[raw] = "no_esco_mapping_or_filtered_out"
            else:
                mapping[raw] = norm

            processed_since_save += 1

            if processed_since_save >= SAVE_EVERY:
                # checkpoint
                progress_out = {
                    "done": sorted(done_set),
                    "mapping": mapping,
                    "dropped": dropped,
                }
                save_json(PROGRESS_PATH, progress_out)
                print(f"Checkpoint saved. Done: {len(done_set)} / {len(raw_skills)}")
                processed_since_save = 0

    # Final save
    progress_out = {
        "done": sorted(done_set),
        "mapping": mapping,
        "dropped": dropped,
    }
    save_json(PROGRESS_PATH, progress_out)

    # Build canonical taxonomy
    canonical = sorted({v["preferred_label"] for v in mapping.values() if v and v.get("preferred_label")})

    save_json(OUT_TAXONOMY, canonical)
    save_json(OUT_MAP, mapping)
    save_json(OUT_DROPPED, dropped)

    print("\n=== DONE ===")
    print(f"Canonical ICT taxonomy size: {len(canonical)}")
    print(f"Mapped entries: {len(mapping)}")
    print(f"Dropped entries: {len(dropped)}")
    print(f"Saved: {OUT_TAXONOMY.resolve()}")
    print(f"Saved: {OUT_MAP.resolve()}")
    print(f"Saved: {OUT_DROPPED.resolve()}")


if __name__ == "__main__":
    main()