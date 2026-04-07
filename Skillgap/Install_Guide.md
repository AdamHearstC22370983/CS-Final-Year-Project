# Skillgap Installation Guide for Examiners

## Overview
This guide explains how to install and run **Skillgap** on a local machine. It assumes the examiner has downloaded the full GitHub repository, has **Docker Desktop** installed and running, and can use a terminal.

Skillgap is a web application consisting of:
* a **React frontend**
* a **FastAPI backend**
* a **PostgreSQL database** running through Docker
* a local processed course catalogue file named **`course_catalogue.json`** used by the recommendation system

The system is designed so that, on first run, the backend can import the local course catalogue into the database if the `courses` table is empty.

---
## 1. Software Requirements
Before running Skillgap, the following should be installed:
### Required software
* **Git**
* **Python 3.11** or compatible version used by the project
* **Node.js** and **npm**
* **Docker Desktop**
* **PostgreSQL client tools** (optional, but useful for verification, I used DBeaver)

### Recommended
* **VSCode** or another code editor
* **pgAdmin** or another PostgreSQL viewer (optional)

---
## 2. Downloading the Project
Clone the repository from GitHub:
```bash
git clone <https://github.com/AdamHearstC22370983/CS-Final-Year-Project>
cd <Skillgap>
```

If the repository is downloaded as a ZIP instead:
1. Extract the ZIP file.
2. Open a terminal in the extracted project folder.

---
## 3. Expected Project Structure

The examiner should ensure that the backend and frontend folders remain in their expected locations.

A typical structure is:
```text
Skillgap/
├── backend/
│   ├── app/
│   │   ├── data/
│   │   │   └── course_catalogue.json
│   │   ├── main.py
│   │   ├── ...
│   ├── library_requirements.txt
│   ├── docker-compose.yaml
│   └── ...
├── frontend/
│   ├── package.json
│   ├── src/
│   └── ...
└── README.md
```

The local course catalogue file **must** be stored at:

```text
backend/app/data/course_catalogue.json
```

---
## 4. Python Environment Setup

Open a terminal in the `backend` folder.

### Create a virtual environment

```bash
python -m venv venv
```

### Activate the virtual environment

I created two different start and stop files for Skillgap to accomodate either Windows or Linux/macOS environments
#### Windows
```bash
venv\Scripts\activate
```

#### macOS / Linux
```bash
source venv/bin/activate
```

### Install required Python libraries
If a `library_requirements.txt` file is included:

```bash
pip install -r library_requirements.txt
```

If needed, the backend typically depends on libraries such as:
* fastapi
* uvicorn
* sqlalchemy
* psycopg2-binary
* python-jose
* passlib
* bcrypt
* python-multipart
* spacy
* scikit-learn
* pydantic
* python-docx
* pymupdf or pdf/text extraction libraries used by the project

Only use the exact versions from the project’s `library_requirements.txt` where available.

---
## 5. Frontend Environment Setup

Open a second terminal in the `frontend` folder.

Install frontend dependencies:
```bash
npm install
```
This will install the packages listed in `package.json`.

---
## 6. Docker and Database Setup

The PostgreSQL database is expected to run through Docker.
Open a terminal in the `backend` folder and run:
```bash
docker compose up -d
```

This starts the PostgreSQL container in the background.
To check that the container is running:
```bash
docker ps
```

---
## 7. Example docker-compose.yaml

If the you need to recreate or verify the Docker setup, a suitable `docker-compose.yaml` for the PostgreSQL database would be:
```yaml
version: '3.9'
services:
  db:
    image: postgres:16
    container_name: skillgap_postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: skillgap_user
      POSTGRES_PASSWORD: skillgap_password
      POSTGRES_DB: skillgap_db
    ports:
      - "54321:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```
If the project already includes its own `docker-compose.yaml`, use that version instead.

---
## 8. Environment Variables

The backend should be configured so that its database connection matches the Docker PostgreSQL settings.

A typical `.env` or equivalent configuration would need values similar to:
```text
DATABASE_URL=postgresql://skillgap_user:skillgap_password@localhost:54321/skillgap_db
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Use the project’s actual values or configuration style if already defined.

---
## 9. Local Course Catalogue Setup

Skillgap uses a processed local course catalogue file for its recommendation system.

### Required file
* `course_catalogue.json`
* Approximate size: **12.8 MB**

### Required location
Store the file here:
```text
backend/app/data/course_catalogue.json
```

### Important
The file must remain in JSON format and keep the expected structure:
```json
{
  "courses": [
    { "url": "...", "course_name": "...", "provider": "..." }
  ]
}
```
The importer expects a top-level `courses` key containing the list of course records.

---
## 10. Importing the Course Catalogue into the Database
The backend is designed so that, on first startup, it can automatically import the contents of `course_catalogue.json` into the database **if the `courses` table is empty**.

This means the examiner should:
1. Ensure Docker is running.
2. Ensure PostgreSQL starts successfully.
3. Ensure `course_catalogue.json` is in the correct location.
4. Start the backend.

If automatic import is enabled correctly in the project, the catalogue should be inserted into the database on first run.

### Manual import option
If automatic import does not run, the project may include a manual backend route such as:
```text
POST /catalog/import-local
```

This can be triggered through the FastAPI docs page after the backend starts:
```text
http://127.0.0.1:8000/docs
```

---
## 11. Starting the Backend
From the `backend` folder, with the virtual environment activated:

```bash
uvicorn app.main:app --reload
```

If the backend starts successfully, it will normally be available at:
```text
http://127.0.0.1:8000
```

The API docs should be available at:
```text
http://127.0.0.1:8000/docs
```

---
## 12. Starting the Frontend
From the `frontend` folder:

```bash
npm run dev
```

The frontend will usually run at:
```text
http://localhost:5173
```

---
## 13. First-Run Workflow for the Examiner

A clean first-run process should be:
1. Clone or extract the Skillgap repository.
2. Place `course_catalogue.json` in `backend/app/data/`.
3. Start Docker Desktop.
4. Run `docker compose up -d` in the `backend` folder.
5. Create and activate the Python virtual environment.
6. Install backend requirements.
7. Install frontend requirements with `npm install`.
8. Start the backend using `uvicorn app.main:app --reload`.
9. Confirm that the course catalogue has been imported automatically, or trigger the manual import route if required.
10. Start the frontend using `npm run dev`.
11. Open the frontend in the browser and use the application normally.

---

## 14. Verifying That the Course Catalogue Imported Correctly
The catalogue import can be verified in any of the following ways:

### Option 1: Check the backend logs
On first run, the backend should show a message indicating that the catalogue was imported or skipped because data already existed.

### Option 2: Check the database directly
Using PostgreSQL tools, confirm that the `courses` table contains records.

For example, in `psql`:
```sql
SELECT COUNT(*) FROM courses;
```

If the import worked, the result should be greater than 0.

### Option 3: Test the recommender through the app
Run a normal skill-gap analysis and confirm that course recommendations are returned.

---
## 15. Troubleshooting

### Backend cannot find `course_catalogue.json`
* Check that the file is stored in `backend/app/data/`
* Check that the backend import code points to the same folder
* Check that the file name is exactly `course_catalogue.json`

### Database connection fails
* Ensure Docker Desktop is running
* Ensure the PostgreSQL container is running
* Ensure the port in `docker-compose.yaml` matches the backend configuration
* Ensure `DATABASE_URL` is correct

### No course recommendations are returned
* Confirm that the `courses` table has been populated
* Confirm that the course catalogue import completed successfully
* Confirm that the recommender is querying the correct database

### Frontend does not load
* Run `npm install` again
* Confirm Node.js is installed
* Check that the frontend is running on the expected port

---

## 16. Suggested Note for Users
Skillgap uses a processed and curated local course catalogue rather than relying on live third-party provider APIs at runtime. 
This was done to improve reproducibility, consistency, and control over the recommendation process. 
The file `course_catalogue.json` must therefore be present and imported correctly for the recommendation system to function as intended.

---

## 17. Recommended Submission Files

To make user setup easier, the repository or submission package should include:
* the full project source code
* `requirements.txt`
* `package.json`
* `docker-compose.yaml`
* `course_catalogue.json`
* this installation guide

If any of these are provided separately, this should be clearly stated in the submission notes.
