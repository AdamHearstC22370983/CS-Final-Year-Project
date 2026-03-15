# entity_storage.py
# Handles saving extracted entities into the database:
# CV entities -> cv_entities table
# JD entities -> jd_entities table

# Entity lists are cleaned and deduplicated before being saved.
from sqlalchemy.orm import Session

from app.models.CV_entity import CVEntity
from app.models.JD_entity import JDEntity


def _clean_entity_name(value) -> str:
    # Normalise entity text so comparisons and duplicate checks are more reliable.
    return str(value or "").strip().lower()


def _clean_entity_type(value) -> str:
    return str(value or "").strip()


def _dedupe_entity_list(entity_list: list) -> list:
    # Remove blank entries and duplicates while preserving order.
    # Duplicates are identified by (entity_name, entity_type).
    cleaned = []
    seen = set()

    for ent in entity_list or []:
        name = _clean_entity_name(ent.get("text"))
        ent_type = _clean_entity_type(ent.get("type"))

        if not name:
            continue

        key = (name, ent_type)
        if key in seen:
            continue

        seen.add(key)
        cleaned.append(
            {
                "text": name,
                "type": ent_type,
            }
        )

    return cleaned

# Save extracted CV entities for a given user.
# A fresh CV analysis should replace the old CV entities for that user.
def save_cv_entities(db: Session, user_id: int, entity_list: list):
    cleaned_entities = _dedupe_entity_list(entity_list)

    try:
        # Remove the previous CV entities for this user so repeated analysis runs
        # do not keep growing the table.
        db.query(CVEntity).filter(CVEntity.user_id == user_id).delete()

        for ent in cleaned_entities:
            cv_ent = CVEntity(
                user_id=user_id,
                entity_name=ent["text"],
                entity_type=ent["type"],
            )
            db.add(cv_ent)

        db.commit()

        return {
            "status": "CV entities saved",
            "user_id": user_id,
            "count": len(cleaned_entities),
        }

    except Exception:
        db.rollback()
        raise

# Save Job Description entities.
# Each new JD upload replaces the previous JD entities globally.
def save_jd_entities(db: Session, entity_list: list):
    cleaned_entities = _dedupe_entity_list(entity_list)

    try:
        # Clear the previously stored JD entities so the next gap analysis
        # only uses the current JD.
        db.query(JDEntity).delete()

        for ent in cleaned_entities:
            jd_ent = JDEntity(
                entity_name=ent["text"],
                entity_type=ent["type"],
            )
            db.add(jd_ent)

        db.commit()

        return {
            "status": "JD entities saved",
            "count": len(cleaned_entities),
        }
    except Exception:
        db.rollback()
        raise