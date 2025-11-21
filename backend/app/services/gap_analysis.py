# gap_analysis.py
# Compares CV entities for a given user against all stored JD entities.
# Finds which JD entities are NOT present in the CV entities and stores them in the missing_entities table.

from sqlalchemy.orm import Session
# Import models
from app.models.CV_entity import CVEntity
from app.models.JD_entity import JDEntity
from app.models.missing_entity import MissingEntity

# Function to compute and store missing entities for a user
def compute_missing_entities(db: Session, user_id: int) -> list:
    # Get user CV entities
    cv_items = db.query(CVEntity.entity_name).filter(CVEntity.user_id == user_id).all()
    cv_set = {x[0].strip().lower() for x in cv_items}

    # Get Job Description entities
    jd_items = db.query(JDEntity.entity_name).all()
    jd_set = {x[0].strip().lower() for x in jd_items}

    # Compute missing items
    missing = list(jd_set - cv_set)
    missing.sort()

    return missing
