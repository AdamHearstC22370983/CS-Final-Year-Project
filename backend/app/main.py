# main.py
# Skillgap backend entry point.
# This FastAPI app handles:
# - user registration
# - user login
# - account data export
# - password change
# - account deletion
# - CV / JD upload and text extraction
# - entity extraction and storage
# - gap analysis
# - entity normalisation
# - local course catalog import and search
# - course recommendations

from pathlib import Path
from typing import Any, List, Optional

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import or_, text

from app.models.CV_entity import CVEntity
from app.models.JD_entity import JDEntity
from app.models.course import Course
from app.models.db import Base, engine, get_db
from app.models.gap_snapshot import GapSnapshot
from app.models.normalised_entity import NormalisedEntity
from app.models.user import User

from app.schemas.user_schema import PasswordChangeRequest, UserCreate, UserLogin

from app.services.ESCO.esco_normaliser import normalise_entity
from app.services.catalog.catalog_ingest import ingest_catalog
from app.services.entity_extraction import extract_entities
from app.services.entity_storage import save_cv_entities, save_jd_entities
from app.services.gap_analysis import compute_missing_entities
from app.services.recommender.course_ranker import rank_courses_for_missing
from app.services.text_extraction import extract_text_from_upload
from app.utils.security import hash_password, verify_password


# Create the FastAPI application instance.
app = FastAPI(
    title="Skillgap Backend API",
    description="API for CV/JD parsing, entity extraction, gap analysis, ESCO-style normalization, and DB-backed course recommendations.",
    version="0.1.0",
)

# Allow the React frontend to call the FastAPI backend during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Development convenience:
# create tables if they do not already exist.
# Note:
# create_all() does not alter existing tables, it only creates missing ones.
Base.metadata.create_all(bind=engine)


# Synonym mapping used to make user-facing missing entities more consistent.
SYNONYMS = {
    "rest": "rest api",
    "restful api": "rest api",
    "golang": "go",
    "g-rpc": "grpc",
    "g rpc": "grpc",
    "k8s": "kubernetes",
}


# Normalise a value into lowercase trimmed text.
def _norm(value: Any) -> str:
    return str(value or "").strip().lower()


# Canonicalise a list of missing entities before returning them to the frontend.
# Duplicate values are removed while preserving order.
# Generic low-value entities are filtered out so the user only sees meaningful gaps.
def _canonicalize_missing_entities(values: List[str]) -> List[str]:
    output: List[str] = []
    seen = set()

    blocked_entities = {
        "initiative",
        "build software",
        "software development",
        "development",
        "coding",
        "programming",
        "teamwork",
        "communication",
        "problem solving",
    }

    for value in values or []:
        cleaned = _norm(value)
        if not cleaned:
            continue

        cleaned = SYNONYMS.get(cleaned, cleaned)

        if cleaned in blocked_entities:
            continue

        if cleaned not in seen:
            seen.add(cleaned)
            output.append(cleaned)

    return output


# Clean organization text before returning it in API responses.
def _clean_organization(value: Any) -> Optional[str]:
    if value is None:
        return None

    text_value = str(value).strip()

    if not text_value:
        return None

    if text_value.startswith("{") and text_value.endswith("}"):
        text_value = text_value[1:-1].strip()

    text_value = text_value.replace('\\"', '"').strip()
    text_value = text_value.strip('"').strip()
    text_value = text_value.replace('"', "").strip()

    return text_value or None


# Root endpoint used as a quick health check.
@app.get("/")
def home():
    return {"message": "Skillgap backend API is running"}


# Simple database test endpoint.
@app.get("/db-test")
def test_database(db=Depends(get_db)):
    result = db.execute(text("SELECT 'Database connection OK' AS status;"))
    return {"database": result.fetchone()[0]}


# Register a new user.
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
        "email": new_user.email,
    }


# Sign in using either username or email plus password.
# This is a simple first-step login flow that returns user identity data.
# A full production version would use JWT or secure server-side sessions.
@app.post("/login")
async def login_user(payload: UserLogin, db=Depends(get_db)):
    identifier = payload.identifier.strip()

    user = (
        db.query(User)
        .filter(
            or_(
                User.username == identifier,
                User.email == identifier,
            )
        )
        .first()
    )

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "message": "Login successful",
        "user": {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
        },
    }


# Return a minimal public-safe user profile by user ID.
# This is useful for restoring frontend session state.
@app.get("/users/{user_id}")
async def get_user_profile(user_id: int, db=Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
    }


# Export the signed-in user's account-related data as JSON-ready content.
# This supports a user-facing "Download My Data" feature.
@app.get("/users/{user_id}/export")
async def export_user_data(user_id: int, db=Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    cv_entities = (
        db.query(CVEntity)
        .filter(CVEntity.user_id == user_id)
        .all()
    )

    normalised_entities = (
        db.query(NormalisedEntity)
        .filter(NormalisedEntity.user_id == user_id)
        .all()
    )

    gap_snapshots = (
        db.query(GapSnapshot)
        .filter(GapSnapshot.user_id == user_id)
        .order_by(GapSnapshot.created_at.desc())
        .all()
    )

    return {
        "account": {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
        },
        "cv_entities": [
            {
                "id": row.id,
                "entity_name": row.entity_name,
            }
            for row in cv_entities
        ],
        "normalised_entities": [
            {
                "id": row.id,
                "original": row.original,
                "normalised": row.normalised,
                "uri": row.uri,
                "source": row.source,
                "entity_type": row.entity_type,
            }
            for row in normalised_entities
        ],
        "gap_snapshots": [
            {
                "id": row.id,
                "missing_entities": row.missing_entities,
                "created_at": row.created_at.isoformat() if row.created_at else None,
            }
            for row in gap_snapshots
        ],
    }


# Change the signed-in user's password.
# This verifies the current password before replacing it with a newly hashed one.
@app.post("/users/{user_id}/change-password")
async def change_user_password(user_id: int, payload: PasswordChangeRequest, db=Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(payload.current_password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Current password is incorrect")

    if not payload.new_password or len(payload.new_password.strip()) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters long")

    user.hashed_password = hash_password(payload.new_password.strip())
    db.commit()

    return {"message": "Password updated successfully"}


# Delete the signed-in user's account and related user-owned data.
# This removes user rows, CV entities, normalised entities, and stored gap snapshots.
@app.delete("/users/{user_id}")
async def delete_user_account(user_id: int, db=Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.query(CVEntity).filter(CVEntity.user_id == user_id).delete()
    db.query(NormalisedEntity).filter(NormalisedEntity.user_id == user_id).delete()
    db.query(GapSnapshot).filter(GapSnapshot.user_id == user_id).delete()
    db.delete(user)
    db.commit()

    return {"message": "Account and related user data deleted successfully"}


# Upload CV endpoint.
@app.post("/upload-cv")
async def upload_cv(file: UploadFile = File(...)):
    contents = await file.read()

    return {
        "filename": file.filename,
        "filesize": len(contents),
        "content_type": file.content_type,
        "status": "CV uploaded successfully",
    }


# Upload Job Description endpoint.
@app.post("/upload-jd")
async def upload_jd(file: UploadFile = File(...)):
    contents = await file.read()

    return {
        "filename": file.filename,
        "filesize": len(contents),
        "content_type": file.content_type,
        "status": "Job Description uploaded successfully",
    }


# Extract raw text from an uploaded file.
@app.post("/extract-text")
async def extract_text(file: UploadFile = File(...)):
    contents = await file.read()
    cleaned_text = extract_text_from_upload(file, contents)

    return {
        "filename": file.filename,
        "text": cleaned_text,
    }


# Extract entities from an uploaded file.
@app.post("/extract-entities")
async def extract_entities_endpoint(file: UploadFile = File(...)):
    contents = await file.read()
    cleaned_text = extract_text_from_upload(file, contents)
    extraction_result = extract_entities(cleaned_text)

    return {
        "filename": file.filename,
        "entities": extraction_result,
    }


# Extract and save CV entities for a specific user.
@app.post("/save-cv-entities")
async def save_cv_entities_endpoint(user_id: int, file: UploadFile = File(...), db=Depends(get_db)):
    contents = await file.read()
    cleaned_text = extract_text_from_upload(file, contents)
    extraction = extract_entities(cleaned_text)

    entity_list = extraction["unique_entities"]
    result = save_cv_entities(db, user_id, entity_list)

    return {
        "saved": result,
        "entities": entity_list,
    }


# Extract and save Job Description entities.
@app.post("/save-jd-entities")
async def save_jd_entities_endpoint(file: UploadFile = File(...), db=Depends(get_db)):
    contents = await file.read()
    cleaned_text = extract_text_from_upload(file, contents)
    extraction = extract_entities(cleaned_text)

    entity_list = extraction["unique_entities"]
    result = save_jd_entities(db, entity_list)

    return {
        "saved": result,
        "entities": entity_list,
    }


# Compute the gap between a user's CV entities and the current JD entities.
@app.post("/compute-gap")
async def compute_gap(user_id: int, db=Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail=f"User with id {user_id} does not exist")

    missing = compute_missing_entities(db, user_id)
    missing = _canonicalize_missing_entities(missing)

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


# Return the latest missing-entity snapshot for a given user.
@app.get("/missing-entities")
async def get_missing_entities(user_id: int, db=Depends(get_db)):
    snapshot = (
        db.query(GapSnapshot)
        .filter(GapSnapshot.user_id == user_id)
        .order_by(GapSnapshot.created_at.desc())
        .first()
    )

    if not snapshot:
        return {
            "user_id": user_id,
            "missing_entities": [],
            "count": 0,
        }

    missing = _canonicalize_missing_entities(snapshot.missing_entities or [])

    return {
        "user_id": user_id,
        "missing_entities": missing,
        "count": len(missing),
        "snapshot_id": snapshot.id,
        "created_at": snapshot.created_at,
    }


# Normalise CV and JD entities using the ESCO-style normaliser.
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
    for original, lowered in raw_entities:
        if lowered not in lower_to_original:
            lower_to_original[lowered] = original

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


# Import the local course catalog JSON file into the database.
@app.post("/catalog/import-local")
def import_catalog_local(db=Depends(get_db)):
    base_dir = Path(".")

    stats = ingest_catalog(
        db=db,
        base_dir=base_dir,
        filename="kaggle_courses.json",
        truncate_first=True,
    )

    return {
        "message": "Catalog import complete",
        "stats": {"kaggle_courses.json": stats},
    }


# Search the local course catalog by query string.
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

    results = []
    for row in rows:
        results.append(
            {
                "url": getattr(row, "url", None),
                "course_name": getattr(row, "course_name", None),
                "provider": getattr(row, "provider", None),
                "organization": _clean_organization(
                    getattr(row, "organization", None) or getattr(row, "organisation", None)
                ),
                "type": getattr(row, "type", None),
                "level": getattr(row, "level", None),
                "subject": getattr(row, "subject", None),
                "duration": getattr(row, "duration", None),
                "rating": getattr(row, "rating", None),
                "nu_reviews": getattr(row, "nu_reviews", None),
                "enrollments": getattr(row, "enrollments", None),
                "skills": getattr(row, "skills", None),
                "skills_norm": getattr(row, "skills_norm", None),
                "description": getattr(row, "description", None),
            }
        )

    return {
        "query": query,
        "count": len(results),
        "results": results,
    }


# Recommend courses for the user's latest missing-entity snapshot.
@app.get("/recommend-courses")
async def recommend_courses(
    user_id: int,
    top_n: int = 10,
    use_cosine: bool = True,
    experience_level: Optional[str] = None,
    has_taken_course: Optional[bool] = None,
    db=Depends(get_db),
):
    snapshot = (
        db.query(GapSnapshot)
        .filter(GapSnapshot.user_id == user_id)
        .order_by(GapSnapshot.created_at.desc())
        .first()
    )

    if not snapshot:
        return {"error": "No gap analysis found. Complete a skill gap test first."}

    missing = _canonicalize_missing_entities(snapshot.missing_entities or [])

    ranked = rank_courses_for_missing(
        db=db,
        missing_entities=missing,
        top_n=top_n,
        use_cosine=use_cosine,
        experience_level=experience_level,
        has_taken_course=has_taken_course,
    )

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