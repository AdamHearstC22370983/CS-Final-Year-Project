# Skillgap – Final Year Project (TU Dublin)
**Student:** Adam Kerslake Hearst  
**Student Number:** C22370983  
**Degree:** BSc (Hons) Computer Science, TU Dublin  
## Overview
Skillgap is a web-based application designed to analyse a user’s CV and a supplied Job Description in order to identify skill gaps and recommend relevant online courses to help the user upskill.

The aim of the project is to bridge the gap between job seekers and suitable online learning resources by providing personalised, data-driven guidance based on the requirements of a target role.

## Current Project Status
Skillgap is currently in active development.
At this stage, the project has moved away from relying on live third-party course provider APIs and instead uses a **locally curated course dataset stored in PostgreSQL**. This change was made to improve:
- stability
- reproducibility
- control over preprocessing
- recommendation consistency
- independence from API limitations and web-scraping issues

The backend pipeline for text extraction, entity extraction, skill-gap analysis, taxonomy building, and local course recommendation is now in place and has been substantially developed.
Frontend UI/UX development is the next major phase.

## What Skillgap Does
After a user creates an account and uploads their CV, Skillgap is designed to:

### 1. Extract text from documents
Skillgap accepts CVs and Job Descriptions and extracts usable text from supported file formats such as:
- PDF
- DOCX

### 2. Perform skill-gap analysis
The backend analyses:
- the user’s uploaded CV
- a target Job Description

It extracts relevant entities such as:
- technical skills
- qualifications
- experience-related terms

It then compares both sets of extracted entities to identify:
- skills or requirements already met
- skills or requirements missing
- areas where upskilling is needed

### 3. Recommend relevant courses
Using a curated local course catalog stored in the database, Skillgap recommends courses that align with the user’s missing skills.

The recommendation pipeline now uses:
- a cleaned active ICT skill taxonomy
- normalized course skills
- ranking logic based on similarity/matching methods such as Jaccard similarity and optional cosine-based text relevance

### 4. Present an upskilling path
The intended user-facing result is a clear list of recommended courses, along with a readable indication of how suitable they are for the user’s identified gaps.

## Current System Scope
### Implemented / In Progress
- user registration
- CV upload
- Job Description upload
- text extraction from CV/JD files
- entity extraction from text
- storage of CV entities and JD entities
- skill-gap computation
- storage of gap snapshots
- locally stored course catalog in PostgreSQL
- skill taxonomy generation and cleaning
- course skill normalisation
- active taxonomy generation
- recommendation ranking backend
- preprocessing pipeline for raw datasets

### Planned / Next Stage
- frontend UI/UX
- guided recommendation questions in the UI
- cleaner recommendation presentation labels instead of exposing raw backend scores
- improved dashboard/results view
- further testing and refinement
- final report polish and deployment packaging

## Technologies Used
### Backend
- **FastAPI** – backend API
- **Python** – main backend language
- **SQLAlchemy** – ORM/database interaction
- **PostgreSQL** – database

### NLP / Matching / Recommendation
- custom entity extraction pipeline
- taxonomy-driven matching
- **scikit-learn** – TF-IDF / cosine similarity components
- set-based similarity scoring such as **Jaccard similarity**

### Document Parsing
- **python-docx**
- **PyPDF2**
- helper utilities for PDF and DOCX text extraction

### Data Preparation / Taxonomy Building
- JSON and CSV preprocessing scripts
- curated ICT taxonomy generation
- course skill normalisation and backfilling

### Frontend (Planned / Next Phase)
- **React.js / Next.js**

### Dev / Tooling
- Git / GitHub
- local preprocessing scripts
- optional future CI/CD with GitHub Actions
- optional future containerisation with Docker

## Important Design Change
Originally, the project planned to use online learning provider APIs such as edX, Udemy, and similar services.
This approach was later replaced with a **database-backed local course catalog** because it offered a more reliable and reproducible workflow for the final year project.
This means the current recommendation engine works from:
- curated local JSON/raw datasets
- a PostgreSQL courses table
- cleaned and normalized course skill metadata
rather than live external APIs.

## How Skillgap Works
### High-Level Flow
1. User registers and logs in  
2. User uploads a CV  
3. User uploads or provides a Job Description  
4. Backend extracts text from both documents  
5. Backend extracts entities such as technical skills, qualifications, and experience  
6. Skill-gap analysis compares CV entities against Job Description entities  
7. Missing skills are identified and stored  
8. Recommendation engine ranks relevant courses from the local database  
9. User receives an upskilling path based on missing skills  

## Current Recommendation Approach
The recommendation system has evolved from simple keyword matching toward a more structured approach.

### Current/Recent Work Includes
- building an ICT-focused active skills taxonomy
- normalising course skills to match the taxonomy
- cleaning invalid or irrelevant skills from course records
- backfilling missing course skills from course title/description text
- ranking candidate courses based on skill overlap and text relevance

### Intended Output to User
Rather than showing raw mathematical similarity scores directly, the final UI is intended to present clearer recommendation labels such as:
- Highly recommended
- Recommended
- Consider

with user-friendly context such as:
- number of missing skills covered
- matched skills
- suitable course level where available

## Data Preprocessing
A separate preprocessing workflow was created to prepare the datasets and taxonomy used by the system.
This includes:
- extracting skill phrases from external datasets
- building and cleaning a skills taxonomy
- merging manually added ICT terms
- filtering raw course data down to ICT-relevant content
- normalising course skills
- building the final active taxonomy used by the backend

A dedicated preprocessing readme has been created:
- `README.data_preprocessing.txt`

This preprocessing workflow is **optional for the external examiner** because the final project will be delivered with a final curated dataset and runtime files.

## Repository Structure
### Runtime Backend
- `app/`
  - `data/`
  - `models/`
  - `schemas/`
  - `services/`
  - `utils/`
  - `main.py`

### Preprocessing
- `data_preprocessing_scripts/`
  - raw datasets
  - preprocessing scripts
  - filtering/normalisation utilities

### Other
- `run_backend.bat`
- project readme files

## Academic Context
This project is completed as part of the TU Dublin Final Year Project module.
Skillgap demonstrates a number of real-world software engineering practices, including:
- requirements analysis
- system and architecture design
- database modelling
- backend API development
- NLP/entity extraction
- recommendation system design
- preprocessing and data cleaning
- iterative refinement of a data-driven software system
- version control and project documentation

## Current Backend Focus
At the current stage of development, the main completed or active backend work includes:
- local course catalog ingestion
- taxonomy cleaning and active taxonomy building
- course skill normalisation
- entity extraction and storage
- gap analysis
- recommendation logic refinement
- preparing the backend for frontend integration

## Future Work
The major remaining work includes:
- frontend UI/UX development
- guided question modal/popup to improve recommendation relevance
- cleaner recommendation result presentation
- additional testing and refinement
- final integration and project submission preparation

## Note for Examiners
The project will be provided in a form that allows the backend to run from curated local data without requiring the full preprocessing pipeline to be rerun.

The preprocessing scripts remain in the repository for:

- transparency
- methodology
- reproducibility
- demonstration of how the final dataset and taxonomy were produced

---

## Summary

Skillgap is a CV and Job Description analysis platform that identifies missing skills and recommends targeted courses using a locally curated and normalized course database.

The project has progressed from an API-based concept into a more robust and reproducible database-backed system, with backend processing and recommendation functionality now substantially implemented and frontend development to follow.
