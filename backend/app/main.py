# Skillgap Backend - FastAPI Starter
# This file initializes the FastAPI application and sets up the first two endpoints.
# These endpoints allow the user to upload:
# CV (PDF/DOCX)
# Job Description (PDF/DOCX)
# For now, the endpoints simply return file information.

from fastapi import FastAPI, Depends, UploadFile, File
from sqlalchemy import text
from app.models.db import get_db
from app.models.db import Base, engine
# now to import the db models so that they are registered with SQLAlchemy
from app.models import user
from app.models import CV_entity
from app.models import JD_entity
from app.models import missing_entity
# import used for text extraction
from app.services.text_extraction import extract_text_from_upload

# creates the main FastAPI application instance
app = FastAPI(
    title="Skillgap Backend API",
    description="API for uploading CV parsing, Job Description parsing, and entity extraction & recommendation.",
    version="0.1.0"
)
# Auto-create tables in PostgreSQL (Dbeaver) (development only)
Base.metadata.create_all(bind=engine)

# Root endpoint to check if the API is running
@app.get("/")
def home():
    return {"message": "Skillgap backend API is running"}
# Can test the endpoint by visiting http://127.0.0.1:8000
# It returns the above message in JSON format

# Upload CV endpoint (POST)
@app.post("/upload-cv")
async def upload_cv(file: UploadFile = File(...)):
# Accepts a CV file (PDF or DOCx).
# The UploadFile object gives access to: filename, filesize, content type and a status.
    contents = await file.read()
    return {
        "filename": file.filename, 
        "filesize": len(contents), 
        "content_type": file.content_type, 
        "status": "CV uploaded successfully"
        }

# Upload Job Description Endpoint (POST)
@app.post("/upload-jd")
async def upload_jd(file: UploadFile = File(...)):
# Accepts a Job Description file (PDF or DOCx).
    contents = await file.read()
    return {
        "filename": file.filename, 
        "filesize": len(contents), 
        "content_type": file.content_type, 
        "status": "Job Description uploaded successfully"
        }

# new endpoint for database connection test
@app.get("/db-test")
def test_database(db=Depends(get_db)):
# Tests connection to the PostgreSQL DB.
# Runs a simple SELECT query.
# Visit: http://127.0.0.1:8000/db-test
    result = db.execute(text("SELECT 'Database connection OK' AS status;"))
    return {"database": result.fetchone()[0]}

@app.post("/extract-text")
async def extract_text(file: UploadFile = File(...)):
# Accepts a CV/Job Description file (PDF or DOCx).
# Extracts and cleans text using the text extraction service.
    contents = await file.read()
    cleaned_text = extract_text_from_upload(file, contents)
    # Returns the cleaned text along with the original filename.
    return { 
        "filename": file.filename, 
        "text": cleaned_text 
        }