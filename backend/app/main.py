# main.py
# Skillgap backend entrypoint
# FastAPI app for user registration, CV/JD processing, gap analysis, normalization, and recommendations

from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from sqlalchemy import text

from app.models.CV_entity import CVEntity
from app.models.JD_entity import JDEntity
from app.models.course import Course
from app.models.db import Base, engine, get_db
from app.models.gap_snapshot import GapSnapshot
from app.models.normalised_entity import NormalisedEntity
from app.models.user import User

from app.schemas.user_schema import UserCreate

from app.services.ESCO.esco_normaliser import normalise_entity
from app.services.catalog.catalog_ingest import ingest_catalog
from app.services.entity_extraction import extract_entities
from app.services.entity_storage import save_cv_entities, save_jd_entities
from app.services.gap_analysis import compute_missing_entities
from app.services.recommender.course_ranker import rank_courses_for_missing
from app.services.text_extraction import extract_text_from_upload
from app.utils.security import hash_password

app = FastAPI(
    title="Skillgap Backend API",
    description="API for CV/JD parsing, entity extraction, gap analysis, ESCO-style normalization, and DB-backed course recommendations.",
    version="0.1.0",
)

# Dev-time convenience
Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {"message": "Skillgap backend API is running"}

@app.get("/db-test")
def test_database(db=Depends(get_db)):
    result = db.execute(text("SELECT 'Database connection OK' AS status;"))
    return {"database": result.fetchone()[0]}

# User registration
@app.post("/register")
async def register_user(payload: UserCreate, db=Depends(get_db)):
    existing_username = db.query(User).filter(User.username == payload.username).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")

    existing_email = db.query(User).filter(User.email == payload.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hash_password(payload.password)

    new_user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hashed,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User created successfully",
        "user_id": new_user.id,
        "username": new_user.username,
    }

# Upload CV endpoint
@app.post("/upload-cv")
async def upload_cv(file: UploadFile = File(...)):
    contents = await file.read()
    return {
        "filename": file.filename,
        "filesize": len(contents),
        "content_type": file.content_type,
        "status": "CV uploaded successfully",
    }
# Upload Job Description endpoint
@app.post("/upload-jd")
async def upload_jd(file: UploadFile = File(...)):
    contents = await file.read()
    return {
        "filename": file.filename,
        "filesize": len(contents),
        "content_type": file.content_type,
        "status": "Job Description uploaded successfully",
    }

# Text extraction enpoint for unit testing
@app.post("/extract-text")
async def extract_text(file: UploadFile = File(...)):
    contents = await file.read()
    cleaned_text = extract_text_from_upload(file, contents)
    return {"filename": file.filename, "text": cleaned_text}

# Entity extraction endpoint for unit testing
@app.post("/extract-entities")
async def extract_entities_endpoint(file: UploadFile = File(...)):
    contents = await file.read()
    cleaned_text = extract_text_from_upload(file, contents)
    extraction_result = extract_entities(cleaned_text)
    return {"filename": file.filename, "entities": extraction_result}

# Save CV entities for unit testing
@app.post("/save-cv-entities")
async def save_cv_entities_endpoint(user_id: int, file: UploadFile = File(...), db=Depends(get_db)):
    contents = await file.read()
    cleaned_text = extract_text_from_upload(file, contents)
    extraction = extract_entities(cleaned_text)
    entity_list = extraction["unique_entities"]
    # before saving, delete existing CV entities for this user to avoid duplicates on repeated uploads
    result = save_cv_entities(db, user_id, entity_list)
    return {"saved": result, "entities": entity_list}

# Save JD entities
@app.post("/save-jd-entities")
async def save_jd_entities_endpoint(file: UploadFile = File(...), db=Depends(get_db)):
    contents = await file.read()
    cleaned_text = extract_text_from_upload(file, contents)
    extraction = extract_entities(cleaned_text)
    entity_list = extraction["unique_entities"]
    # before saving, delete existing Job Description entities for this user to avoid duplicates on repeated uploads
    result = save_jd_entities(db, entity_list)
    return {"saved": result, "entities": entity_list}

# Compute skill gap between CV and Job Description entities and save a snapshot of the missing entities for this user in the database
@app.post("/compute-gap")
async def compute_gap(user_id: int, db=Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail=f"User with id {user_id} does not exist")

    missing = compute_missing_entities(db, user_id)

    snapshot = GapSnapshot(user_id=user_id, missing_entities=missing)
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)

    return {
        "user_id": user_id,
        "missing_entities": missing,
        "count": len(missing),
        "snapshot_id": snapshot.id,
    }

# Get latest missing entities
@app.get("/missing-entities")
async def get_missing_entities(user_id: int, db=Depends(get_db)):
    snapshot = (
        db.query(GapSnapshot)
        .filter(GapSnapshot.user_id == user_id)
        .order_by(GapSnapshot.created_at.desc())
        .first()
    )
    if not snapshot:
        return {"user_id": user_id, "missing_entities": [], "count": 0}
    # return the missing entities along with snapshot metadata
    return {
        "user_id": user_id,
        "missing_entities": snapshot.missing_entities,
        "count": len(snapshot.missing_entities),
        "snapshot_id": snapshot.id,
        "created_at": snapshot.created_at,
    }

# Normalize entities using ESCO-style normalisation and save the results in the database
@app.post("/normalise-entities")
async def normalise_entities(user_id: int, db=Depends(get_db)):
    db.query(NormalisedEntity).filter(NormalisedEntity.user_id == user_id).delete()
    db.commit()

    cv_entities = db.query(CVEntity.entity_name).filter(CVEntity.user_id == user_id).all()
    jd_entities = db.query(JDEntity.entity_name).all()

    raw_entities = [(x[0], x[0].strip().lower()) for x in cv_entities] + [
        (x[0], x[0].strip().lower()) for x in jd_entities
    ]
    # to avoid normalising the same entity numerous times if it appears in both CV and JD,
    # we create a mapping of lowercased entities to their original form and only normalise unique lowercased entities
    lower_to_original = {}
    for original, lowered in raw_entities:
        if lowered not in lower_to_original:
            lower_to_original[lowered] = original

    unique_original_entities = list(lower_to_original.values())
    # normalise each unique entity and save the results
    normalised_records = []
    for original_entity in unique_original_entities:
        result = normalise_entity(original_entity)

        entry = NormalisedEntity(
            user_id=user_id,
            original=result["original"],
            normalised=result["normalised"],
            uri=result["uri"],
            source=result["source"],
            entity_type=result["type"],
        )
        db.add(entry)
        normalised_records.append(result)

    db.commit()

    return {
        "user_id": user_id,
        "normalised_entities": normalised_records,
        "count": len(normalised_records),
    }

# Import local catalog data from a JSON file into the database
@app.post("/catalog/import-local")
def import_catalog_local(db=Depends(get_db)):
    base_dir = Path(".")
    stats = ingest_catalog(
        db=db,
        base_dir=base_dir,
        filename="kaggle_courses.json",
        truncate_first=True,
    )
    # return a response indicating the import is complete
    return {
        "message": "Catalog import complete",
        "stats": {"kaggle_courses.json": stats},
    }

# Search local catalog
@app.get("/catalog/search")
def search_catalog(query: str, limit: int = 10, db=Depends(get_db)):
    q = f"%{query.lower()}%"

    rows = (
        db.query(Course)
        .filter(
            (Course.course_name.ilike(q)) |
            (Course.description.ilike(q)) |
            (Course.provider.ilike(q))
        )
        .limit(limit)
        .all()
    )

    return {
        "query": query,
        "count": len(rows),
        "results": [
            {
                "url": getattr(r, "url", None),
                "course_name": getattr(r, "course_name", None),
                "provider": getattr(r, "provider", None),
                "organization": getattr(r, "organization", None) or getattr(r, "organisation", None),
                "type": getattr(r, "type", None),
                "level": getattr(r, "level", None),
                "subject": getattr(r, "subject", None),
                "duration": getattr(r, "duration", None),
                "rating": getattr(r, "rating", None),
                "nu_reviews": getattr(r, "nu_reviews", None),
                "enrollments": getattr(r, "enrollments", None),
                "skills": getattr(r, "skills", None),
                "skills_norm": getattr(r, "skills_norm", None),
                "description": getattr(r, "description", None),
            }
            for r in rows
        ],
    }

# Recommend courses
@app.get("/recommend-courses")
async def recommend_courses(
    user_id: int,
    top_n: int = 10,
    use_cosine: bool = True,
    experience_level: Optional[str] = None,
    has_taken_course: Optional[bool] = None,
    db=Depends(get_db),
):
    # Guided-question support:
    # - experience_level can be Beginner / Intermediate / Advanced
    # - has_taken_course can be true / false
    # If experience_level is omitted and has_taken_course=false,
    # the ranker infers Beginner internally
    snapshot = (
        db.query(GapSnapshot)
        .filter(GapSnapshot.user_id == user_id)
        .order_by(GapSnapshot.created_at.desc())
        .first()
    )
    if not snapshot:
        return {"error": "No gap analysis found. Complete a skill gap test first."}
    missing = snapshot.missing_entities or []
    # Call the ranker with the missing entities and optional filters to get ranked course recommendations.
    ranked = rank_courses_for_missing(
        db=db,
        missing_entities=missing,
        top_n=top_n,
        use_cosine=use_cosine,
        experience_level=experience_level,
        has_taken_course=has_taken_course,
    )
    # Only include optional fields in the API response if they are consistently present in the top results to avoid sparse data in the response
    return {
        "user_id": user_id,
        "missing_entities": missing,
        "missing_count": len(missing),
        "top_n": top_n,
        "use_cosine": use_cosine,
        "experience_level": experience_level,
        "has_taken_course": has_taken_course,
        "recommendations": ranked,
    }
