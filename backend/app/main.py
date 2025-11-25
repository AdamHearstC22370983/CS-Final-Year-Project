# Skillgap Backend - FastAPI Starter
# This file initializes the FastAPI application and sets up various endpoint for unit and integration testing.
from fastapi import FastAPI, Depends, UploadFile, File
from sqlalchemy import text
from app.models.db import get_db
from app.models.db import Base, engine
# now to import the db models so that they are registered with SQLAlchemy
from app.models import user
# imports used for text extraction
from app.services.text_extraction import extract_text_from_upload
from app.services.entity_extraction import extract_entities
# import used to save entities
from app.services.entity_storage import save_cv_entities, save_jd_entities
# imports used registration and password hashing
from fastapi import HTTPException
from app.models.user import User
from app.utils.security import hash_password
# importing a Pydantic schema for user registration
from app.schemas.user_schema import UserCreate
# imports for gap analysis
from app.services.gap_analysis import compute_missing_entities
# import for gap snapshot
from app.models.gap_snapshot import GapSnapshot
# import for ESCO normalisation
from app.services.ESCO.esco_normaliser import normalise_entity
from app.models.normalised_entity import NormalisedEntity
from app.models.CV_entity import CVEntity
from app.models.JD_entity import JDEntity
# imports for course recommendation
from app.services.recommender.course_recommender import COURSE_DB
# Visit: http://127.0.0.1:8000/db-test for database connection test
# Visit: http://127.0.0.1:8000/docs for automatic API docs (Swagger UI)

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

# endpoint for user registration (POST)
@app.post("/register")
async def register_user(payload: UserCreate, db=Depends(get_db)):
# Registers a new user using a JSON body.
# Fixes the bcrypt >72 bytes issue and prevents URL encoding bugs.
# Password is hashed for security.
# Plan to create authentication endpoints later but not needed in FR.
    
    # Check for existing username
    existing_username = db.query(User).filter(User.username == payload.username).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")

    # Check for existing email
    existing_email = db.query(User).filter(User.email == payload.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password safely
    hashed = hash_password(payload.password)
    new_user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hashed
    )
    # Save new user to DB
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    # Return success message
    return {
        "message": "User created successfully",
        "user_id": new_user.id,
        "username": new_user.username
    }
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
    result = db.execute(text("SELECT 'Database connection OK' AS status;"))
    return {"database": result.fetchone()[0]}

# endpioint to extract text from uploaded file
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
# endpoint to extract entities from text
@app.post("/extract-entities")
async def extract_entities_endpoint(file: UploadFile = File(...)):
    # Upload a CV or JD, extract text, and then extract entities from that text.
    contents = await file.read()
    # extract and clean text
    cleaned_text = extract_text_from_upload(file, contents)

    # extract rule-based entities
    extraction_result = extract_entities(cleaned_text)

    return{
        "filename": file.filename,
        "entities": extraction_result
    }

# endpoints to save CV entities
@app.post("/save-cv-entities")
async def save_cv_entities_endpoint(
    user_id: int,
    file: UploadFile = File(...),
    db=Depends(get_db)
):    
    # Upload a CV, extract entities, and save them to the cv_entities table.
    contents = await file.read()
    # Extract text
    cleaned_text = extract_text_from_upload(file, contents)

    # Extract entities from text
    extraction = extract_entities(cleaned_text)
    entity_list = extraction["unique_entities"]

    # Save entities to DB
    result = save_cv_entities(db, user_id, entity_list)
    return {
        "saved": result,
        "entities": entity_list
    }
# endpoint to save JD entities
@app.post("/save-jd-entities")
async def save_jd_entities_endpoint(
    file: UploadFile = File(...),
    db=Depends(get_db)
):
    # Upload a Job Description, extract entities, and save them to the jd_entities table.
    contents = await file.read()
    # Extract text
    cleaned_text = extract_text_from_upload(file, contents)

    # Extract entities from text
    extraction = extract_entities(cleaned_text)
    entity_list = extraction["unique_entities"]

    # Save entities to DB
    result = save_jd_entities(db, entity_list)
    return {
        "saved": result,
        "entities": entity_list
    }

# endpoint to compute and store gap analysis
@app.post("/compute-gap")
async def compute_gap(user_id: int, db=Depends(get_db)):
    # Ensure the user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail=f"User with id {user_id} does not exist")
    # Compute the missing entities
    missing = compute_missing_entities(db, user_id)

    # Store snapshot in DB
    snapshot = GapSnapshot(
        user_id = user_id,
        missing_entities = missing  # this is a Python list
    )
    # Save to DB, commit, and refresh to get the ID
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    # Return the result
    return {
        "user_id": user_id,
        "missing_entities": missing,
        "count": len(missing),
        "snapshot_id": snapshot.id
    }

# endpoint to retrieve missing entities for a user via a snapshot
@app.get("/missing-entities")
async def get_missing_entities(user_id: int, db=Depends(get_db)):
    snapshot = (
        db.query(GapSnapshot)
        .filter(GapSnapshot.user_id == user_id)
        .order_by(GapSnapshot.created_at.desc())
        .first()
    )
    # If no snapshot found, return empty list
    if not snapshot:
        return {"user_id": user_id, "missing_entities": [], "count": 0}
    # Return the missing entities from the latest snapshot
    return {
        "user_id": user_id,
        "missing_entities": snapshot.missing_entities,
        "count": len(snapshot.missing_entities),
        "snapshot_id": snapshot.id,
        "created_at": snapshot.created_at
    }
# endpoint to normalise entities via ESCO
@app.post("/normalise-entities")
async def normalise_entities(user_id: int, db=Depends(get_db)):
    # Remove all previous records for this user before new fetching
    db.query(NormalisedEntity).filter(
        NormalisedEntity.user_id == user_id
    ).delete()
    db.commit()

    # Fetch CV + JD entities
    cv_entities = db.query(CVEntity.entity_name).filter(
        CVEntity.user_id == user_id
    ).all()
    jd_entities = db.query(JDEntity.entity_name).all()

    # raw_entities = [("Java", "java"), ("Python", "python"), ...]
    raw_entities = [
        (x[0], x[0].strip().lower()) for x in cv_entities
    ] + [
        (x[0], x[0].strip().lower()) for x in jd_entities
    ]

    # Deduplicate using lowercase, but preserve original case
    lower_to_original = {}
    for orig, low in raw_entities:
        if low not in lower_to_original:
            lower_to_original[low] = orig

    unique_original_entities = list(lower_to_original.values())

    normalised_records = []

    # Normalise each unique entity
    for original_entity in unique_original_entities:
        result = normalise_entity(original_entity)
        # Create NormalisedEntity record
        entry = NormalisedEntity(
            user_id=user_id,
            original=result["original"],
            normalised=result["normalised"],
            uri=result["uri"],
            source=result["source"],
            entity_type=result["type"]
        )
        # Save to DB
        db.add(entry)
        normalised_records.append(result)
    db.commit()
    # Return all normalised records
    return {
        "user_id": user_id,
        "normalised_entities": normalised_records,
        "count": len(normalised_records)
    }
# endpoint to recommend courses based off of the most recent skill gap snapshot
@app.get("/recommend-courses")
async def recommend_courses(user_id: int, db=Depends(get_db)):
# Fetch most recent skill gap snapshot for this user
    snapshot = (
        db.query(GapSnapshot)
        .filter(GapSnapshot.user_id == user_id)
        .order_by(GapSnapshot.created_at.desc())
        .first()
    )
    # If no snapshot is found, return an error message
    if not snapshot:
        return {"error": "No gap analysis found. Complete a skill gap test first."}
    missing = snapshot.missing_entities   # list of skill names (strings)

    # Load static course database (JSON)
    recommendations = {}

    # Match only missing skills to JSON keys
    for skill in missing:
        key = skill.lower()   # ensure lowercase for matching

        if key in COURSE_DB:
            # Add course list to recommendations output
            recommendations[skill] = COURSE_DB[key]
    # Return formatted response
    return {
        "user_id": user_id,
        "missing_entities": missing,
        "recommendations": recommendations,
        "total_skills_covered": len(recommendations)
    }
