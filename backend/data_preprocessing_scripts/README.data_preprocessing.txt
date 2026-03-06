# Data Preprocessing Guide
Overview
This directory contains the one-off preprocessing scripts and source datasets used to prepare the local course catalog and ICT skills taxonomy for the Skillgap backend.

The purpose of this preprocessing pipeline was to:
- extract a broad ICT-related skills library from external datasets
- normalise those skills into a more controlled taxonomy
- reduce a large raw course dataset to a smaller ICT-focused catalog
- align course skills with the same taxonomy used by the backend recommender

This preprocessing workflow is **optional for the external examiner**.

A final curated dataset will be provided separately before final project submission, so the examiner does **not** need to rerun every preprocessing step in order to run the working system. These scripts are included primarily for:
- transparency
- reproducibility
- showing how the final dataset and taxonomy were produced

In other words:
- **To run the finished backend:** use the final curated dataset and runtime files provided in `app/data/`
- **To reproduce or inspect the preprocessing methodology:** use the scripts in this folder
## Folder Structure
backend/
  app/
    data/
      skill_taxonomy_it_active.json
      skill_taxonomy_it_active_stats.json
      skill_taxonomy_map.json
      taxonomy_dropped.json
      active_taxonomy_additions.json
      original_unfiltered_skill_taxonomy_it.json
      deprecated_skill_taxonomy_it_active.json
  -------------------------------
    other folders included in /app
  -------------------------------
  data_preprocessing_scripts/
    raw_data/
      JobsDatasetProcessed.csv
      processed_coursera_data.json
      processed_coursera_data_sanitized.json
      processed_coursera_data_ICT.ndjson
      processed_coursera_data_ICT_stats.json
    extract_unique_skills.py
    build_taxonomy_from_kaggle_skills.py
    merge_active_taxonomy.py
    normalise_course_skills.py
    build_active_taxonomy.py
    clean_skills_norm_to_active_taxonomy.py
    backfill_skills_norm_from_course_text.py
    filter_coursera_ict_batch.py
  
------------------------ Important Notes -------------------------------
Running these scripts is optional
The final system will be provided with a final curated dataset and runtime taxonomy files. This means the backend can be run directly without regenerating the taxonomy or re-filtering the source data.

These scripts are included for reproducibility
If desired, the examiner can inspect or rerun parts of the preprocessing pipeline to understand how the final course catalog and taxonomy were created.

Results may not be perfectly identical if rerun from raw data
This is because the catalog reduction process involved a combination of:
- automated filtering
- taxonomy merging
- course skill normalisation
- manual review/removal of irrelevant courses
Therefore, rerunning the scripts from raw data may produce results that are close to, but not necessarily identical to, the final curated dataset used by the backend.

Source-of-truth for runtime
The backend runtime depends primarily on the files in:
backend/app/data/
  
The most important runtime taxonomy file is:
app/data/skill_taxonomy_it_active.json
  
Preprocessing Objectives
--------------------------
The preprocessing workflow aimed to solve four problems:

A. Raw skill phrases were noisy
The external jobs dataset contained many repeated, generic, and non-technical phrases. These needed to be extracted, deduplicated, and filtered.

B. Raw course data was too large and too broad
The raw Coursera-derived dataset contained many courses outside the intended ICT/software umbrella.

C. Course skills and extracted CV/JD skills needed to align
The recommender works best when both the course catalog and user/job skills use the same terminology.

D. Only relevant and teachable skills should remain
The final taxonomy was restricted to skills that were useful for the project’s ICT recommendation use case.

Raw Input Files
raw_data/JobsDatasetProcessed.csv
This is the jobs dataset used to extract a broad skills library from the IT Skills column.
Used for:
- generating a raw skills library
- building the initial taxonomy
  
raw_data/processed_coursera_data.json
This is the original large Coursera-derived source file.
Used for reducing the course dataset to ICT-only entries

raw_data/processed_coursera_data_sanitized.json
This is a cleaned version of the Coursera file where invalid JSON values such as NaN were replaced so that the file could be parsed safely in batches.
Used for streaming/batch ICT filtering

raw_data/processed_coursera_data_ICT.ndjson
This is the filtered ICT-only course output generated from the Coursera source file.
Used for creating a smaller, more relevant course subset

raw_data/processed_coursera_data_ICT_stats.json
This contains statistics for the ICT filtering step, such as:
- total processed
- kept
- dropped

Runtime Taxonomy and Support Files
These files are generated or maintained during preprocessing and then used by the backend.

app/data/skill_taxonomy_it_active.json
The final active ICT taxonomy used by the backend for:
- skill extraction
- skill matching
- recommender filtering
- cleaning skills_norm
This is the main taxonomy file used at runtime.

app/data/skill_taxonomy_it_active_stats.json
Statistics about the active taxonomy after intersection/cleanup.

app/data/skill_taxonomy_map.json
Mapping file from raw skill phrases to cleaned/canonical skill labels.

app/data/taxonomy_dropped.json
A record of terms that were removed during taxonomy filtering/cleanup.

app/data/active_taxonomy_additions.json
A manually curated list of additional useful ICT terms added to improve coverage of technologies and tools not captured well enough by the original taxonomy.

app/data/original_unfiltered_skill_taxonomy_it.json
An earlier broad taxonomy before later filtering and cleanup.

app/data/deprecated_skill_taxonomy_it_active.json
A previous active taxonomy snapshot kept for reference.

Script-by-Script Explanation
extract_unique_skills.py
Purpose: Extracts and deduplicates raw skill phrases from the jobs dataset.
Input
  - raw_data/JobsDatasetProcessed.csv
Main process
- Reads the IT Skills column
- Parses cell contents
- Normalises strings
- Removes duplicates
Output
Typically produces a raw deduplicated skills list used for later taxonomy-building.
This is the earliest step in building the project’s ICT skills vocabulary.

build_taxonomy_from_kaggle_skills.py
Purpose: Builds a more structured taxonomy from the raw extracted skills.
Input
- output from the raw skill extraction stage
- supporting taxonomy/normalisation logic
Main process
- cleans the raw skill list
- normalises terms
- produces a filtered skill taxonomy
- records dropped terms
Output
- app/data/original_unfiltered_skill_taxonomy_it.json
- app/data/skill_taxonomy_map.json
- app/data/taxonomy_dropped.json
This transforms a noisy raw skill library into something more useful for backend matching.

merge_active_taxonomy.py
Purpose: Merges the current active taxonomy with manually-added ICT terms.
Input
- app/data/skill_taxonomy_it_active.json
- app/data/active_taxonomy_additions.json
Main process
- reads both lists
- normalises entries
- merges them
- removes duplicates
Output
An updated/merged active taxonomy file.
This allowed useful modern ICT terms and specific technologies to be added even if they were not well represented in the original extracted taxonomy.

normalise_course_skills.py
Purpose: Normalises the skills field in the course database to produce skills_norm.
Input
- course rows from the database
- taxonomy mapping file
Main process
- reads each course’s raw skills
- maps raw terms to cleaned taxonomy labels
- writes canonical values back into skills_norm
Output
Database update by populating the column "courses.skills_norm".
This is the key alignment step that allows:
- user/job skills
- course skills
to be compared in a common label space.

build_active_taxonomy.py
Purpose: Builds a reduced active taxonomy based on what is actually present in the course catalog.
Input
- broad taxonomy
- database course skills
Main process:
- gathers distinct normalised skills from the DB
- intersects them with the broader ICT taxonomy
- produces the runtime active taxonomy
Output:
- app/data/skill_taxonomy_it_active.json
- app/data/skill_taxonomy_it_active_stats.json
This makes the final taxonomy smaller, cleaner, and more relevant to the actual local course catalog.

clean_skills_norm_to_active_taxonomy.py
Purpose: Cleans the database skills_norm field so that it only contains skills permitted by the active taxonomy.
Input:
- app/data/skill_taxonomy_it_active.json
- courses.skills_norm
Main process:
- checks each course’s skills_norm
- removes entries not present in the active taxonomy
- updates the database
Output:
- Database cleanup:removes invalid or irrelevant skills from skills_norm
This prevents noisy or non-ICT labels from affecting recommendation quality.

backfill_skills_norm_from_course_text.py
Purpose: Backfills missing skills_norm values using the course title and description.
Input:
- courses table
- app/data/skill_taxonomy_it_active.json
Main process:
- scans course text
- matches terms from the active taxonomy
- writes those matches to skills_norm where empty
Output: Database updated, fills previously empty skills_norm rows
This improves coverage for recommendations when a course has useful descriptive text but incomplete raw skill metadata.

filter_coursera_ict_batch.py
Purpose: Reduces the large Coursera source file to an ICT-only subset.
Input
- raw_data/processed_coursera_data.json
- app/data/skill_taxonomy_it_active.json
Main process
- sanitises invalid JSON values such as NaN
- streams the file in batches
- keeps only courses matching the active ICT taxonomy and/or fallback ICT keywords
- writes filtered courses as NDJSON

Output
- raw_data/processed_coursera_data_sanitized.json
- raw_data/processed_coursera_data_ICT.ndjson
- raw_data/processed_coursera_data_ICT_stats.json
This was used to reduce a large raw Coursera export to a smaller, more relevant ICT-focused course set.

Practical Use Cases
Option A — Run the final backend only
This involves everything in the backend/app folder and its sub-directories.
the final backend code
the final taxonomy files in app/data/
the final curated dataset provided with the submission

This is the easiest and most stable way to run the project.

Option B — Inspect or rerun preprocessing steps
This is optional.
This can be done to understand how the data was prepared, but it is not required to run the final system.

Recommended Reproduction Order
To reproduce the preprocessing logic approximately, the broad order is:
1. extract_unique_skills.py
2. build_taxonomy_from_kaggle_skills.py
3. merge_active_taxonomy.py
4. normalise_course_skills.py
5. build_active_taxonomy.py
6. clean_skills_norm_to_active_taxonomy.py
7. backfill_skills_norm_from_course_text.py
8. filter_coursera_ict_batch.py

This order reflects the general logic used during development.

-------------- Important Limitation -----------------
The final database-sized catalog was not produced by automation alone.
The overall reduction from the larger raw catalog down to the smaller working database involved:
- automated filtering
- taxonomy cleaning
- skill normalisation
- manual review and removal of irrelevant records

Therefore, rerunning the scripts from raw data may produce:
a similar result or a closely related result but not necessarily a perfectly identical final catalog
For this reason, the final curated dataset will be supplied separately before final project submission.

------------- Notes on Reproducibility ------------
This project includes the preprocessing scripts for transparency and academic reproducibility, but the final system is intended to be run from the curated artefacts rather than regenerated from scratch every time.

The main runtime files the backend depends on are:
- app/data/skill_taxonomy_it_active.json
- app/data/skill_taxonomy_map.json

These are the files that matter most for executing the final system.
Temporary cache files such as esco_cache.json or temporary progress files such as taxonomy_progress.json are large local-only intermediary artefacts not needed to run the final backend.
  
The preprocessing pipeline was exploratory and iterative with multiple intermediate files being  retained in order to document how the final taxonomy and course catalog were produced. 
The final system, however, will be delivered with the necessary curated data so that the external examiner can run the backend without needing to rerun the full preprocessing chain.
