# course_ranker.py
# app/services/recommender/course_ranker.py
from app.services.recommender.priority_engine import (compute_dynamic_priority, missing_boost)
# function to look at course level
def infer_course_level(title: str):
# Basic inference of course level based on title wording.
    t = title.lower()
    # looks a course difficulties and adds them in the ranking process
    if any(w in t for w in ["beginner", "introduction", "fundamentals"]):
        return 3
    if "intermediate" in t:
        return 2
    if "advanced" in t:
        return 1
    return 2  # default mid-level

# function to compute the score of courses to find the most relevant one to the user.
def compute_score(skill: str, course: dict, jd_entities: list, missing_list: list):
# Final score = difficulty + JD frequency priority + missing skill boost + popularity
    return (
        infer_course_level(course["title"]) +
        compute_dynamic_priority(skill, jd_entities) +  # depends on JD
        missing_boost(skill, missing_list) +            # depends on CV vs JD gap
        course.get("popularity", 0)                     # optional field
    )

def rank_courses(skill: str, course_list: list, jd_entities: list, missing_list: list):
    # Rank course list for a specific skill.
    scored = []
    # loops for each course in the list and scores it based on criteria
    for course in course_list:
        score = compute_score(skill, course, jd_entities, missing_list)
        scored.append((score, course))
    # sorts the courses
    scored.sort(reverse=True, key=lambda x: x[0])
    # returns the courses, 3 most suitable per missing skill
    return [course for (_, course) in scored[:3]]