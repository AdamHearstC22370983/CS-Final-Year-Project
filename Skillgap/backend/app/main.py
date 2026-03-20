# main.py
# Skillgap backend entry point.
# This FastAPI app handles:
# - user registration
# - user login with JWT access tokens
# - account data export
# - password change
# - account deletion
# - history retrieval for stored gap snapshots
# - CV / JD upload and text extraction
# - manual skill confirmation post-analysis
# - entity extraction and storage
# - gap analysis
# - entity normalisation
# - local course catalog import and search
# - course recommendations

from pathlib import Path
from typing import Any, List, Optional

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy import text

from app.models.CV_entity import CVEntity
from app.models.JD_entity import JDEntity
from app.models.confirmed_skill import ConfirmedSkill
from app.models.course import Course
from app.models.db import Base, engine, get_db
from app.models.gap_snapshot import GapSnapshot
from app.models.normalised_entity import NormalisedEntity
from app.models.user import User
from app.schemas.user_schema import (
    PasswordChangeRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
)
from app.services.ESCO.esco_normaliser import normalise_entity
from app.services.catalog.catalog_ingest import ingest_catalog
from app.services.entity_extraction import extract_entities
from app.services.entity_storage import save_cv_entities, save_jd_entities
from app.services.gap_analysis import compute_missing_entities
from app.services.recommender.course_ranker import rank_courses_for_missing
from app.services.text_extraction import extract_text_from_upload
from app.utils.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)

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

# create tables if they do not already exist.
# create_all() only creates missing tables. It does not alter existing ones.
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
# OAuth2 bearer token scheme for JWT auth.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
security = HTTPBearer()

# Request body for confirmed-skill actions.
class ConfirmedSkillRequest(BaseModel):
    skill_name: str

# Validate password strength during registration and password change.
def _validate_password_strength(password: str) -> str:
    cleaned = (password or "").strip()

    if len(cleaned) < 10:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 10 characters long",
        )

    has_upper = any(ch.isupper() for ch in cleaned)
    has_lower = any(ch.islower() for ch in cleaned)
    has_digit = any(ch.isdigit() for ch in cleaned)

    if not (has_upper and has_lower and has_digit):
        raise HTTPException(
            status_code=400,
            detail="Password must include at least one uppercase letter, one lowercase letter, and one number",
        )

    return cleaned

# Resolve the currently authenticated user from the JWT token.
# Resolve the signed-in user from the bearer token.
def _get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db=Depends(get_db),
):
    token = credentials.credentials
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(status_code=401, detail="Token missing user subject")

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token subject")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

# Normalise a value into lowercase trimmed text.
def _norm(value: Any) -> str:
    return str(value or "").strip().lower()

# Canonicalise missing entities before returning them to the frontend.
# Duplicate values are removed while preserving order.
# Generic low-value entities are filtered out.
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
        "collaboration",
        "problem solving",
    }
    # for loop to iterate through values, clena and canonicalise them
    # then add them to the output list bar they are not blocked entities or duplicates
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

# Return a user's confirmed skills as a canonicalised set.
def _get_confirmed_skill_set(db, user_id: int) -> set[str]:
    rows = (
        db.query(ConfirmedSkill.skill_name)
        .filter(ConfirmedSkill.user_id == user_id)
        .all()
    )
    # variable confirmed is a set of cleaned and canonicalised skill names that the user has manually confirmed they have, used to adjust the missing-entity list returned to the frontend
    confirmed = set()
    # for loop to iterate through the rows and add the cleaned and canonicalised skill names to the confirmed set
    for row in rows:
        value = _norm(row[0])
        if not value:
            continue
        # apply synonym mapping to the value
        value = SYNONYMS.get(value, value)
        confirmed.add(value)

    return confirmed

# Remove confirmed skills from a missing-entity list after canonicalisation.
def _apply_confirmed_skill_adjustments(db, user_id: int, missing_values: List[str]) -> List[str]:
    canonical_missing = _canonicalize_missing_entities(missing_values)
    confirmed = _get_confirmed_skill_set(db, user_id)

    if not confirmed:
        return canonical_missing
    # return a list of values that are in canonical_missing but not in confirmed
    return [value for value in canonical_missing if value not in confirmed]

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

# Run heavy file parsing in a worker thread.
def _extract_text_sync(upload_file, contents: bytes) -> str:
    return extract_text_from_upload(upload_file, contents)


# Run heavy NLP/entity extraction in a worker thread.
def _extract_entities_sync(cleaned_text: str) -> dict:
    return extract_entities(cleaned_text)


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
    username = payload.username.strip()
    email = payload.email.strip().lower()
    password = payload.password

    if len(password.encode("utf-8")) > 72:
        raise HTTPException(
            status_code=400,
            detail="Password is too long. Please use a shorter password.",
        )

    existing_user = (
        db.query(User)
        .filter((User.username == username) | (User.email == email))
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username or email already exists",
        )

    new_user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}

# Sign in using either username or email plus password.
@app.post("/login", response_model=TokenResponse)
async def login_user(payload: UserLogin, db=Depends(get_db)):
    identifier = payload.identifier.strip()

    user = (
        db.query(User)
        .filter((User.username == identifier) | (User.email == identifier))
        .first()
    )

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username/email or password")

    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        },
    }

# Return the signed-in user's profile.
@app.get("/me")
async def get_me(current_user: User = Depends(_get_current_user)):
    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
    }

# Return the signed-in user's stored gap-analysis history.
@app.get("/me/history")
async def get_user_history(current_user: User = Depends(_get_current_user), db=Depends(get_db)):
    snapshots = (
        db.query(GapSnapshot)
        .filter(GapSnapshot.user_id == current_user.id)
        .order_by(GapSnapshot.created_at.desc())
        .all()
    )
    # history variable is a list of dicts with snapshot_id, created_at, missing_entities, and missing_count
    history = []
    for snapshot in snapshots:
        missing_entities = _apply_confirmed_skill_adjustments(
            db, current_user.id, snapshot.missing_entities or []
        )
        history.append(
            {
                "snapshot_id": snapshot.id,
                "created_at": snapshot.created_at.isoformat() if snapshot.created_at else None,
                "missing_entities": missing_entities,
                "missing_count": len(missing_entities),
            }
        )

    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "history": history,
        "history_count": len(history),
    }

# Export the signed-in user's account-related data.
@app.get("/me/export")
async def export_user_data(current_user: User = Depends(_get_current_user), db=Depends(get_db)):
    cv_entities = db.query(CVEntity).filter(CVEntity.user_id == current_user.id).all()
    normalised_entities = (
        db.query(NormalisedEntity).filter(NormalisedEntity.user_id == current_user.id).all()
    )
    gap_snapshots = (
        db.query(GapSnapshot)
        .filter(GapSnapshot.user_id == current_user.id)
        .order_by(GapSnapshot.created_at.desc())
        .all()
    )
    confirmed_skills = (
        db.query(ConfirmedSkill)
        .filter(ConfirmedSkill.user_id == current_user.id)
        .order_by(ConfirmedSkill.skill_name.asc())
        .all()
    )

    return {
        "account": {
            "user_id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
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
        "confirmed_skills": [
            {
                "id": row.id,
                "skill_name": row.skill_name,
                "created_at": row.created_at.isoformat() if row.created_at else None,
            }
            for row in confirmed_skills
        ],
    }

# Change the signed-in user's password.
@app.post("/me/change-password")
async def change_user_password(
    payload: PasswordChangeRequest,
    current_user: User = Depends(_get_current_user),
    db=Depends(get_db),
):
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(status_code=401, detail="Current password is incorrect")

    new_password = _validate_password_strength(payload.new_password)
    current_user.hashed_password = hash_password(new_password)
    db.commit()

    return {"message": "Password updated successfully"}

# Delete the signed-in user's account and related user-owned data.
# Delete the signed-in user account and all user-linked data.
@app.delete("/me")
async def delete_my_account(
    current_user: User = Depends(_get_current_user),
    db=Depends(get_db),
):
    try:
        # Delete user-linked child rows first to satisfy foreign key constraints.
        db.query(GapSnapshot).filter(
            GapSnapshot.user_id == current_user.id
        ).delete()

        db.query(ConfirmedSkill).filter(
            ConfirmedSkill.user_id == current_user.id
        ).delete()

        db.query(NormalisedEntity).filter(
            NormalisedEntity.user_id == current_user.id
        ).delete()

        db.query(CVEntity).filter(
            CVEntity.user_id == current_user.id
        ).delete()

        # Finally delete the user row itself.
        db.query(User).filter(
            User.id == current_user.id
        ).delete()

        db.commit()

        return {"message": "Account and related user data deleted successfully"}

    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete account")

# Lightweight upload test endpoint for CV files.
@app.post("/upload-cv")
async def upload_cv(file: UploadFile = File(...)):
    contents = await file.read()

    return {
        "filename": file.filename,
        "filesize": len(contents),
        "content_type": file.content_type,
        "status": "CV uploaded successfully",
    }

# Lightweight upload test endpoint for job-description files.
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

# Extract and save CV entities for the signed-in user.
@app.post("/analysis/save-cv-entities")
async def save_cv_entities_endpoint(
    file: UploadFile = File(...),
    current_user: User = Depends(_get_current_user),
    db=Depends(get_db),
):
    contents = await file.read()

    cleaned_text = await run_in_threadpool(_extract_text_sync, file, contents)
    extraction = await run_in_threadpool(_extract_entities_sync, cleaned_text)

    entity_list = extraction.get("unique_entities", [])
    result = save_cv_entities(db, current_user.id, entity_list)

    return {
        "saved": result,
        "entities": entity_list,
    }

# Extract and save the current job-description entities.
@app.post("/analysis/save-jd-entities")
async def save_jd_entities_endpoint(
    file: UploadFile = File(...),
    current_user: User = Depends(_get_current_user),
    db=Depends(get_db),
):
    contents = await file.read()

    cleaned_text = await run_in_threadpool(_extract_text_sync, file, contents)
    extraction = await run_in_threadpool(_extract_entities_sync, cleaned_text)

    entity_list = extraction.get("unique_entities", [])
    result = save_jd_entities(db, entity_list)

    return {
        "saved": result,
        "entities": entity_list,
    }

# Compute the current gap for the signed-in user.
@app.post("/analysis/compute-gap")
async def compute_gap(current_user: User = Depends(_get_current_user), db=Depends(get_db)):
    missing = compute_missing_entities(db, current_user.id)
    missing = _apply_confirmed_skill_adjustments(db, current_user.id, missing)

    snapshot = GapSnapshot(user_id=current_user.id, missing_entities=missing)
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)

    return {
        "user_id": current_user.id,
        "missing_entities": missing,
        "count": len(missing),
        "snapshot_id": snapshot.id,
    }

# Return the latest missing-entity snapshot for the signed-in user.
@app.get("/analysis/missing-entities")
async def get_missing_entities(current_user: User = Depends(_get_current_user), db=Depends(get_db)):
    snapshot = (
        db.query(GapSnapshot)
        .filter(GapSnapshot.user_id == current_user.id)
        .order_by(GapSnapshot.created_at.desc())
        .first()
    )

    if not snapshot:
        return {
            "user_id": current_user.id,
            "missing_entities": [],
            "count": 0,
        }

    missing = _apply_confirmed_skill_adjustments(
        db, current_user.id, snapshot.missing_entities or []
    )

    return {
        "user_id": current_user.id,
        "missing_entities": missing,
        "count": len(missing),
        "snapshot_id": snapshot.id,
        "created_at": snapshot.created_at,
    }

# Return the signed-in user's manually confirmed skills.
@app.get("/me/confirmed-skills")
async def get_confirmed_skills(
    current_user: User = Depends(_get_current_user),
    db=Depends(get_db),
):
    rows = (
        db.query(ConfirmedSkill)
        .filter(ConfirmedSkill.user_id == current_user.id)
        .order_by(ConfirmedSkill.skill_name.asc())
        .all()
    )

    skills = []
    for row in rows:
        value = _norm(row.skill_name)
        value = SYNONYMS.get(value, value)
        if value:
            skills.append(value)

    deduped = []
    seen = set()
    for skill in skills:
        if skill not in seen:
            seen.add(skill)
            deduped.append(skill)

    return {
        "user_id": current_user.id,
        "confirmed_skills": deduped,
        "count": len(deduped),
    }

# Manually confirm that the signed-in user already has a skill.
@app.post("/me/confirmed-skills")
async def add_confirmed_skill(
    payload: ConfirmedSkillRequest,
    current_user: User = Depends(_get_current_user),
    db=Depends(get_db),
):
    skill_name = _norm(payload.skill_name)
    skill_name = SYNONYMS.get(skill_name, skill_name)

    if not skill_name:
        raise HTTPException(status_code=400, detail="Skill name is required")

    existing = (
        db.query(ConfirmedSkill)
        .filter(
            ConfirmedSkill.user_id == current_user.id,
            ConfirmedSkill.skill_name == skill_name,
        )
        .first()
    )

    if existing:
        return {
            "message": "Skill already confirmed",
            "user_id": current_user.id,
            "skill_name": skill_name,
        }

    row = ConfirmedSkill(
        user_id=current_user.id,
        skill_name=skill_name,
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    return {
        "message": "Skill confirmed successfully",
        "user_id": current_user.id,
        "skill_name": skill_name,
        "id": row.id,
    }

# Undo or remove a previously confirmed skill for the signed-in user.
@app.delete("/me/confirmed-skills")
async def remove_confirmed_skill(
    skill_name: str,
    current_user: User = Depends(_get_current_user),
    db=Depends(get_db),
):
    cleaned_skill = _norm(skill_name)
    cleaned_skill = SYNONYMS.get(cleaned_skill, cleaned_skill)

    row = (
        db.query(ConfirmedSkill)
        .filter(
            ConfirmedSkill.user_id == current_user.id,
            ConfirmedSkill.skill_name == cleaned_skill,
        )
        .first()
    )

    if not row:
        raise HTTPException(status_code=404, detail="Confirmed skill not found")

    db.delete(row)
    db.commit()

    return {
        "message": "Confirmed skill removed",
        "user_id": current_user.id,
        "skill_name": cleaned_skill,
    }

# Normalise CV and JD entities for a given user.
@app.post("/normalise-entities")
async def normalise_entities(
    current_user: User = Depends(_get_current_user),
    db=Depends(get_db),
):
    # Remove any previous normalised records for this signed-in user
    # so each run reflects the latest CV + JD state.
    db.query(NormalisedEntity).filter(
        NormalisedEntity.user_id == current_user.id
    ).delete()
    db.commit()

    # Get the current user's CV entities.
    cv_entities = (
        db.query(CVEntity.entity_name)
        .filter(CVEntity.user_id == current_user.id)
        .all()
    )

    # JD entities are still treated as the current shared target JD set.
    jd_entities = db.query(JDEntity.entity_name).all()

    # Combine CV and JD entities into one list while also preparing a lowered form
    # for duplicate removal.
    raw_entities = []

    for row in cv_entities:
        original = str(row[0] or "").strip()
        lowered = original.lower()

        if original:
            raw_entities.append((original, lowered))

    for row in jd_entities:
        original = str(row[0] or "").strip()
        lowered = original.lower()

        if original:
            raw_entities.append((original, lowered))

    # Remove duplicates while preserving the first original version seen.
    lower_to_original = {}

    for original, lowered in raw_entities:
        if lowered not in lower_to_original:
            lower_to_original[lowered] = original

    unique_original_entities = list(lower_to_original.values())

    # Normalise each unique entity and save the result for this signed-in user.
    normalised_records = []

    for original_entity in unique_original_entities:
        result = normalise_entity(original_entity)

        entry = NormalisedEntity(
            user_id=current_user.id,
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
        "message": "Entities normalised successfully",
        "user_id": current_user.id,
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
    # Only return the fields that are relevant for course recommendation
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

# Recommend courses for the signed-in user's latest missing-entity snapshot.
@app.get("/analysis/recommend-courses")
async def recommend_courses(
    top_n: int = 10,
    use_cosine: bool = True,
    experience_level: Optional[str] = None,
    has_taken_course: Optional[bool] = None,
    current_user: User = Depends(_get_current_user),
    db=Depends(get_db),
):
    snapshot = (
        db.query(GapSnapshot)
        .filter(GapSnapshot.user_id == current_user.id)
        .order_by(GapSnapshot.created_at.desc())
        .first()
    )

    if not snapshot:
        return {"error": "No gap analysis found. Complete a skill gap test first."}

    missing = _apply_confirmed_skill_adjustments(
        db, current_user.id, snapshot.missing_entities or []
    )
    # variable ranked is a list of dicts with course information
    ranked = rank_courses_for_missing(
        db=db,
        missing_entities=missing,
        top_n=top_n,
        use_cosine=use_cosine,
        experience_level=experience_level,
        has_taken_course=has_taken_course,
    )

    return {
        "user_id": current_user.id,
        "missing_entities": missing,
        "missing_count": len(missing),
        "top_n": top_n,
        "use_cosine": use_cosine,
        "experience_level": experience_level,
        "has_taken_course": has_taken_course,
        "recommendations": ranked,
    }