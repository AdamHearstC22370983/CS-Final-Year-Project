# Skillgap

---
### Student Number: C22370983
### Name: Adam Kerslake Hearst
### TU Dublin - TU856/4

Skillgap is a full-stack web application designed to help users identify skill gaps between their CV and a target job description, then recommend relevant online courses to help address those gaps.

The project was developed as a practical employability and upskilling tool, with a particular focus on ICT-related roles. It allows users to upload a CV and job description, extract and compare relevant entities from both documents, identify missing skills, and receive ranked course recommendations from a curated local course catalogue.

---

## Current Project Status

Skillgap is now in a its final state, with both the analytical workflow and the user-facing application working together as a complete system.

Recent improvements include:
- JWT-based authentication and protected user routes
- refined backend route structure for analysis, history, and account features
- manual confirmed-skills feature with undo support
- history page for stored skill-gap snapshots
- improved results flow and frontend usability
- cleaner light/dark mode support and UI consistency
- curated local course catalogue integrated into the recommender
- ESCO-assisted skill normalisation with caching support
- local catalogue import support for reproducible recommendation behaviour

The main runnable version of the project is contained in the **`Skillgap/`** directory.

Older backend/frontend versions have been retained in the repository for reference, but previous stages of the project can also be recovered through the Git commit history.

---

## Features

### Core analysis flow
- Upload CV documents in supported formats
- Upload or paste a target job description
- Extract relevant entities and skills from both documents
- Compare CV and job description content to identify missing skills
- Recommend relevant courses from a curated local catalogue
- Refresh recommendations after user confirmation of skills

### User account features
- Register and log in securely
- JWT-based authenticated session handling
- Access protected user-specific analysis features
- View profile-linked data
- Manage user account actions

### Results and refinement
- View detected missing skills
- Manually confirm skills already possessed but not present in the CV
- Undo confirmed skills
- Improve recommendation relevance through adjusted gap results

### Tracking and persistence
- Store user-linked gap snapshots
- View analysis history
- Revisit previous analysis results

### UI and usability
- Responsive React frontend
- Light and dark mode support
- Cleaner navigation and improved page consistency
- Guided and user-friendly results presentation

---

## Tech Stack

### Backend
- FastAPI
- SQLAlchemy
- PostgreSQL
- Passlib / bcrypt
- JWT authentication
- spaCy
- scikit-learn

### Frontend
- React
- Bootstrap
- Axios

### Other project elements
- Document upload and text extraction utilities
- Active taxonomy-based entity extraction
- ESCO-assisted skill normalisation
- Local course catalogue and recommendation ranking logic
- Gap snapshot and history storage
- Docker-based PostgreSQL setup

---

## Recommendation Approach

Skillgap uses a **content-based recommendation approach** rather than relying on live third-party provider APIs at runtime.

The recommendation process is based on:
- identified missing skills from the CV/job description comparison
- a curated local course catalogue stored in PostgreSQL
- course metadata and normalised skill fields
- similarity-based ranking using direct skill overlap and optional text-based relevance scoring

This approach was chosen to improve reliability, reproducibility, and control over the recommendation process.

---

## Local Course Catalogue

Skillgap uses a processed local JSON catalogue file named:

```text
course_catalogue.json
