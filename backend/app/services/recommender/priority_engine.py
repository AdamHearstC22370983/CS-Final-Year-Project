# priority_engine.py
# app/services/recommender/priority_engine.py

def compute_dynamic_priority(skill: str, jd_entities: list):
# Computes a dynamic priority score based on how often a skill appears in the job description entity list.
    skill = skill.lower()
    count = sum(1 for e in jd_entities if e.lower() == skill)
    # priority is weighed based on how much it is mentioned in a JD
    if count >= 3:
        return 3    # high priority skill emphasized repeatedly
    elif count == 2:
        return 2    # medium priority
    elif count == 1:
        return 1    # low priority
    else:
        return 0    # not in JD → base priority only

# skills listed in the user's "missing entities" gets an added bonus
def missing_boost(skill: str, missing_list: list):
    if skill.lower() in missing_list: 
        return 3
    else: 
        return 0