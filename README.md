# Skillgap
---
### Student Number: C22370983
### Name: Adam Kerslake Hearst
### TU Dublin - TU856/4
Skillgap is a full-stack web application that helps users identify skill gaps between their CV and a target job description, then recommends relevant courses to help bridge those gaps.

The project is designed as an MVP focused on practical upskilling:
- upload a CV
- upload a job description
- extract entities/skills from both
- compare them to find missing skills
- recommend courses from a local catalogue
- allow users to manually confirm skills they already have but did not include in their CV

---

## Current Project Status

Skillgap is now in a very good presentation state.

Recent improvements include:
- JWT-based login and authenticated user routes
- cleaner `/me` and `/analysis` backend route structure
- manual confirmed-skills feature with undo support
- history page for stored gap snapshots
- export and delete account actions
- improved dark mode and frontend consistency
- launcher scripts for easier local startup

The main runnable version of the project is now contained in the **`Skillgap/`** directory.

Older backend/frontend versions have been retained in the repository for reference, but previous states of the project can also be recovered through the Git commit history.

---

## Features

### Core analysis flow
- Upload CV documents
- Upload job descriptions
- Extract skills/entities from both documents
- Compute missing skills
- Recommend relevant learning resources

### User account features
- Register and log in securely
- JWT-based authenticated session handling
- Change password
- Export user-linked data
- Delete account

### Results and refinement
- View detected missing skills
- Manually confirm skills already possessed
- Undo confirmed skills
- Refresh recommendations based on adjusted gaps

### Tracking
- View analysis history
- Store gap snapshots per user

### UI
- Responsive React frontend
- Light and dark mode support
- Cleaner navigation and page consistency

---

## Tech Stack

### Backend
- FastAPI
- SQLAlchemy
- PostgreSQL
- Passlib / bcrypt
- JWT authentication

### Frontend
- React
- Bootstrap
- Axios

### Other project elements
- Entity extraction and text parsing utilities
- Local course catalogue and ranking logic
- ESCO-related normalisation utilities

---

## Project Structure

The main runnable project is inside:

```text
Skillgap/
