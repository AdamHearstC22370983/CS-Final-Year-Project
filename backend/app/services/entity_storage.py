# entity_storage.py
# Handles saving extracted entities into the database:
# CV entities → cv_entities table
# JD entities → jd_entities table

from sqlalchemy.orm import Session
from app.models.CV_entity import CVEntity
from app.models.JD_entity import JDEntity
from app.models.missing_entity import MissingEntity

# Saves extracted CV entities for a given user.
def save_cv_entities(db: Session, user_id: int, entity_list: list):
    # entity_list is a list of dicts with 'text' and 'type' keys
    for ent in entity_list:
        cv_ent = CVEntity(
            user_id=user_id,
            entity_name=ent["text"],
            entity_type=ent["type"]
        )
        db.add(cv_ent)
    # Commits to the db    
    db.commit()
    return {"status": "CV entities saved"}


# Saves Job Description entities.
def save_jd_entities(db: Session, entity_list: list):
#   No user_id required as the Job Description belongs to a job posting.
    # entity_list
    for ent in entity_list:
        jd_ent = JDEntity(
            entity_name=ent["text"],
            entity_type=ent["type"]
        )
        db.add(jd_ent)

    db.commit()
    return {"status": "JD entities saved"}
