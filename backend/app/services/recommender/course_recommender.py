# course_recommender.py
import json
import os
# Loads a static JSON dataset containing mapped courses for different technical skills.
# This file exposes COURSE_DB, which the /recommend-courses endpoint imports dynamically when needed.

def load_course_db():
# Loads the static courses.json file from the same folder.
# Returns: dict: {"skill_name": [course_list] }
# It raises a FileNotFoundError if the JSON file is missing.
    
    # Get the directory where the file is located
    dir_path = os.path.dirname(__file__)

    # Build the path to courses.json inside the same folder
    file_path = os.path.join(dir_path, "courses.json")
    # Ensure courses.json exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"ERROR: courses.json not found at: {file_path}")
    # Load and return JSON content
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
    
# Load the static course database once when module is imported.
# This is what the recommender endpoint uses.
COURSE_DB = load_course_db()
