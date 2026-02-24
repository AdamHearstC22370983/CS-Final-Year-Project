# Skillgap Backend - FastAPI
# Main application entrypoint (DB-backed course catalog + CV/JD parsing pipeline)

from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from sqlalchemy import text
from pathlib import Path

from app.models.db import get_db, Base, engine

# Import DB models to ensure SQLAlchemy registers them for create_all()
from app.models.user import User
from app.models.CV_entity import CVEntity
from app.models.JD_entity import JDEntity
from app.models.gap_snapshot import GapSnapshot
from app.models.normalised_entity import NormalisedEntity
from app.models.course import Course

# Services
from app.utils.security import hash_password
from app.schemas.user_schema import UserCreate

from app.services.text_extraction import extract_text_from_upload
from app.services.entity_extraction import extract_entities
from app.services.entity_storage import save_cv_entities, save_jd_entities
from app.services.gap_analysis import compute_missing_entities
from app.services.ESCO.esco_normaliser import normalise_entity

# Catalog ingestion (admin task, not runtime)
from app.services.catalog.catalog_ingest import ingest_catalog

app = FastAPI(
    title="Skillgap Backend API",
    description="API for CV/JD parsing, entity extraction, gap analysis, ESCO normalisation, and DB-backed course recommendations.",
    version="0.1.0",
)

# Dev-only: auto-create tables
Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {"message": "Skillgap backend API is running"}


@app.get("/db-test")
def test_database(db=Depends(get_db)):
    result = db.execute(text("SELECT 'Database connection OK' AS status;"))
    return {"database": result.fetchone()[0]}


# ---------------------------
# Auth (registration only)
# ---------------------------
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


# ---------------------------
# Upload + Extraction
# ---------------------------
@app.post("/upload-cv")
async def upload_cv(file: UploadFile = File(...)):
    contents = await file.read()
    return {
        "filename": file.filename,
        "filesize": len(contents),
        "content_type": file.content_type,
        "status": "CV uploaded successfully",
    }


@app.post("/upload-jd")
async def upload_jd(file: UploadFile = File(...)):
    contents = await file.read()
    return {
        "filename": file.filename,
        "filesize": len(contents),
        "content_type": file.content_type,
        "status": "Job Description uploaded successfully",
    }


@app.post("/extract-text")
async def extract_text(file: UploadFile = File(...)):
    contents = await file.read()
    cleaned_text = extract_text_from_upload(file, contents)
    return {"filename": file.filename, "text": cleaned_text}


@app.post("/extract-entities")
async def extract_entities_endpoint(file: UploadFile = File(...)):
    contents = await file.read()
    cleaned_text = extract_text_from_upload(file, contents)
    extraction_result = extract_entities(cleaned_text)
    return {"filename": file.filename, "entities": extraction_result}


# ---------------------------
# Entity Storage
# ---------------------------
@app.post("/save-cv-entities")
async def save_cv_entities_endpoint(user_id: int, file: UploadFile = File(...), db=Depends(get_db)):
    contents = await file.read()
    cleaned_text = extract_text_from_upload(file, contents)
    extraction = extract_entities(cleaned_text)
    entity_list = extraction["unique_entities"]

    result = save_cv_entities(db, user_id, entity_list)
    return {"saved": result, "entities": entity_list}


@app.post("/save-jd-entities")
async def save_jd_entities_endpoint(file: UploadFile = File(...), db=Depends(get_db)):
    contents = await file.read()
    cleaned_text = extract_text_from_upload(file, contents)
    extraction = extract_entities(cleaned_text)
    entity_list = extraction["unique_entities"]

    result = save_jd_entities(db, entity_list)
    return {"saved": result, "entities": entity_list}

# ---------------------------
# Gap Analysis + Snapshots
# ---------------------------
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

    return {
        "user_id": user_id,
        "missing_entities": snapshot.missing_entities,
        "count": len(snapshot.missing_entities),
        "snapshot_id": snapshot.id,
        "created_at": snapshot.created_at,
    }

# ---------------------------
# ESCO Normalisation
# ---------------------------
@app.post("/normalise-entities")
async def normalise_entities(user_id: int, db=Depends(get_db)):
    db.query(NormalisedEntity).filter(NormalisedEntity.user_id == user_id).delete()
    db.commit()

    cv_entities = db.query(CVEntity.entity_name).filter(CVEntity.user_id == user_id).all()
    jd_entities = db.query(JDEntity.entity_name).all()

    raw_entities = [(x[0], x[0].strip().lower()) for x in cv_entities] + [
        (x[0], x[0].strip().lower()) for x in jd_entities
    ]

    lower_to_original = {}
    for orig, low in raw_entities:
        if low not in lower_to_original:
            lower_to_original[low] = orig

    unique_original_entities = list(lower_to_original.values())

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
# ---------------------------
# Catalog (DB-backed)
# ---------------------------
@app.post("/catalog/import-local")
def import_catalog_local(db=Depends(get_db)):
    base_dir = Path(".")
    stats = ingest_catalog(
        db=db,
        base_dir=base_dir,
        filename="kaggle_courses.json",
        truncate_first=True,
    )
    return {"message": "Catalog import complete", "stats": {"kaggle_courses.json": stats}}


@app.get("/catalog/search")
def search_catalog(query: str, limit: int = 10, db=Depends(get_db)):
    q = f"%{query.lower()}%"
    rows = (
        db.query(Course)
        .filter(
            (Course.course_name.ilike(q)) |
            (Course.description.ilike(q)) |
            (Course.provider.ilike(q)) |
            (Course.organization.ilike(q))
        )
        .limit(limit)
        .all()
    )

    return {
        "query": query,
        "count": len(rows),
        "results": [
            {
                "url": r.url,
                "course_name": r.course_name,
                "provider": r.provider,
                "organization": r.organization,
                "type": r.type,
                "level": r.level,
                "subject": r.subject,
                "Duration": r.duration,
                "rating": r.rating,
                "nu_reviews": r.nu_reviews,
                "enrollments": r.enrollments,
                "skills": r.skills,
                "description": r.description,
            }
            for r in rows
        ],
    }
# ---------------------------
# Recommendations (DB-backed)
# ---------------------------
@app.get("/recommend-courses")
async def recommend_courses(user_id: int, limit_per_skill: int = 5, db=Depends(get_db)):
    snapshot = (
        db.query(GapSnapshot)
        .filter(GapSnapshot.user_id == user_id)
        .order_by(GapSnapshot.created_at.desc())
        .first()
    )

    if not snapshot:
        return {"error": "No gap analysis found. Complete a skill gap test first."}

    missing = snapshot.missing_entities
    recommendations = {}

    for skill in missing:
        like = f"%{skill.lower()}%"

        # Candidate selection: match by skill name in skills JSON, title, or description
        candidates = (
            db.query(Course)
            .filter(
                (Course.course_name.ilike(like)) |
                (Course.description.ilike(like)) |
                (Course.skills.cast(str).ilike(like))
            )
            .limit(limit_per_skill)
            .all()
        )

        if candidates:
            recommendations[skill] = [
                {
                    "url": c.url,
                    "course_name": c.course_name,
                    "provider": c.provider,
                    "organization": c.organization,
                    "type": c.type,
                    "level": c.level,
                    "subject": c.subject,
                    "Duration": c.duration,
                    "rating": c.rating,
                    "nu_reviews": c.nu_reviews,
                    "enrollments": c.enrollments,
                    "skills": c.skills,
                }
                for c in candidates
            ]

    return {
        "user_id": user_id,
        "missing_entities": missing,
        "recommendations": recommendations,
        "total_skills_covered": len(recommendations),
    }
