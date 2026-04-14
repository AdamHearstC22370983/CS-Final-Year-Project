# gap_analysis.py
# Compares the current user's CV entities against the current stored JD entities.
# Finds which JD entities are NOT present in the CV entities.
# CV entities are scoped to the user.
# JD entities are treated as the single current job description.
from sqlalchemy.orm import Session
from app.models.CV_entity import CVEntity
from app.models.JD_entity import JDEntity

def _norm(value) -> str:
    return str(value or "").strip().lower()

# Compute missing entities for a given user.
def compute_missing_entities(db: Session, user_id: int) -> list:
    # Get the current user's CV entities.
    cv_items = (
        db.query(CVEntity.entity_name)
        .filter(CVEntity.user_id == user_id)
        .all()
    )
    cv_set = {_norm(row[0]) for row in cv_items if _norm(row[0])}

    # Get the current JD entities.
    jd_items = db.query(JDEntity.entity_name).all()
    jd_set = {_norm(row[0]) for row in jd_items if _norm(row[0])}
    # If there is no JD loaded, there is nothing to compare against.
    if not jd_set:
        return []
    # If there is no CV loaded for the user, then everything in the JD is missing.
    if not cv_set:
        missing = list(jd_set)
        missing.sort()
        return missing

    missing = list(jd_set - cv_set)
    missing.sort()

    return missing