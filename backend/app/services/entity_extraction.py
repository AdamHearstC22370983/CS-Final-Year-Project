# entity_extraction.py

# This module performs:
# Basic NLP preprocessing
# Rule-based entity extraction
# Produces ESCO-ready entity candidates

#This is *not* the final ESCO version.
#It prepares standardised "entity candidates" for ESCO lookup later.
import re
import spacy

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")


# Text preprocessing function
def preprocess_text(text: str) -> str:
#    Cleans and normalises text for entity extraction.
#    make letters lowercase, strip whitespace and remove excessive punctuation

    text = text.lower()
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text


# Below are simple keyword lists and patterns for rule-based extraction.
# In a production system, these would be more comprehensive or replaced with ML models.
TECH_KEYWORDS = [
    "python", "java", "javascript", "c#", "c++", "sql", "html", "css",
    "react", "node", "docker", "kubernetes", "linux", "git", "aws",
    "azure", "gcp", "tensorflow", "pytorch", "postgresql", "mongodb",
]

QUALIFICATION_KEYWORDS = [
    "degree", "bachelor", "masters", "phd", "diploma", "certificate",
    "certification", "msc", "bsc"
]

SOFT_SKILLS = [
    "communication", "teamwork", "presentation", "leadership",
    "time management", "problem solving", "critical thinking"
]

EXPERIENCE_PATTERNS = [
    r"\b[0-9]+ ?\+? years? experience\b",
    r"\bexperience with\b",
    r"\bworked on\b",
    r"\bfamiliar with\b"
]

def extract_rule_based_entities(text: str) -> list:
#   Extract technical skills, qualifications, and soft skills using pattern matching + keyword checking.
    entities = []
    cleaned = preprocess_text(text)

    # Tokenise with spaCy
    doc = nlp(cleaned)

    # Keyword-based extraction
    for token in doc:
        if token.text in TECH_KEYWORDS:
            entities.append({"text": token.text, "type": "technical"})
        if token.text in SOFT_SKILLS:
            entities.append({"text": token.text, "type": "soft"})
        if token.text in QUALIFICATION_KEYWORDS:
            entities.append({"text": token.text, "type": "qualification"})

    # Experience extraction (regex)
    for pattern in EXPERIENCE_PATTERNS:
        matches = re.findall(pattern, cleaned)
        for match in matches:
            entities.append({"text": match, "type": "experience"})

    return entities

# main extraction function
def extract_entities(cleaned_text: str) -> dict:
#    High-level extraction function.
#    Returns a dictionary with:
#    raw_entities: rule-based raw hits
#    unique_entities: deduplicated entity list
#    esco_ready: full normalised list for ESCO API lookup

    raw_entities = extract_rule_based_entities(cleaned_text)

    # Deduplicate
    seen = set()
    unique = []
    for ent in raw_entities:
        key = ent["text"]
        if key not in seen:
            unique.append(ent)
            seen.add(key)

    # Prepare ESCO-ready format
    esco_prepared = []
    for ent in unique:
        esco_prepared.append({
            "original": ent["text"],
            "lookup_term": ent["text"],
            "type": ent["type"],
            "ready_for_esco": True
        })

    return {
        "raw_entities": raw_entities,
        "unique_entities": unique,
        "esco_ready_entities": esco_prepared
    }
