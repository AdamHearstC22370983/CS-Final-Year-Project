# Skillgap Backend - FastAPI Starter
# This file initializes the FastAPI application and sets up the first two endpoints.
# These endpoints allow the user to upload:
# CV (PDF/DOCX)
# Job Description (PDF/DOCX)
# For now, the endpoints simply return file information.

from fastapi import FastAPI, UploadFile, File

#creates the main FastAPI application instance
app = FastAPI(
    title="Skillgap Backend API",
    description="API for uploading CV parsing, Job Description parsing, and entity extraction & recommendation.",
    version="0.1.0"
)
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
    return {"filename": file.filename, "filesize": len(contents), "content_type": file.content_type, "status": "CV uploaded successfully"}

# Upload Job Description Endpoint (POST)
@app.post("/upload-jd")
async def upload_jd(file: UploadFile = File(...)):
# Accepts a Job Description file (PDF or DOCx).
    contents = await file.read()
    return {"filename": file.filename, "filesize": len(contents), "content_type": file.content_type, "status": "Job Description uploaded successfully"}

