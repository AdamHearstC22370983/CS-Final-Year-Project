# gap_analysis.py
# Compares CV entities for a given user against all stored JD entities.
# Finds which JD entities are NOT present in the CV entities and stores them in the missing_entities table.

from sqlalchemy.orm import Session
# Import models
from app.models.CV_entity import CVEntity
from app.models.JD_entity import JDEntity
from app.models.missing_entity import MissingEntity


def compute_and_store_gap(db: Session, user_id: int):
# For a given user_id:
# Load all CV & JD entities
# Identify which JD entities are missing from that user's CV
# Store the result in missing_entities

    # Returns a list of missing entity names.
    # Get all entities from the user's CV
    cv_rows = db.query(CVEntity).filter(CVEntity.user_id == user_id).all()
    cv_entity_set = {row.entity_name.strip().lower() for row in cv_rows}

    # Get all JD entities (MVP: using all JDs stored in the system)
    jd_rows = db.query(JDEntity).all()

    # Clean old gaps for this user (so the table reflects the latest comparison)
    db.query(MissingEntity).filter(MissingEntity.user_id == user_id).delete()
    # intialise list to hold names of missing entities
    missing_entities = []
    for jd in jd_rows:
        jd_name_norm = jd.entity_name.strip().lower()

        # If this JD entity isn't present in the CV entity set, it's a gap
        if jd_name_norm not in cv_entity_set:
            gap = MissingEntity(
                user_id=user_id,
                jd_entity_id=jd.id,
                entity_name=jd.entity_name,
            )
            db.add(gap)
            missing_entities.append(jd.entity_name)
    # Commit all new missing entities to the DB
    db.commit()
    return missing_entities
