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
# I used Copilot to help add more keywords to the list but I wish to use an API key here to extract from ESCO directly.
TECH_KEYWORDS = [
    "python", "java", "javascript", "c#", "c++", "sql", "html", "css",
    "react", "node", "docker", "kubernetes", "linux", "git", "aws",
    "azure", "gcp", "tensorflow", "pytorch", "postgresql", "mongodb",
    "ruby", "php", "swift", "go", "typescript", "django", "flask",
    "spring", "angular", "vue", "rest", "graphql", "api", "microservices",
    "agile", "scrum", "devops", "ci/cd", "jira", "confluence", "jenkins",
    "ansible", "terraform", "helm", "bash", "powershell", "selenium",
    "jupyter", "notebook", "data science", "machine learning", "deep learning",
    "artificial intelligence", "nlp", "computer vision", "big data", "hadoop", "spark",
    "etl", "data analysis", "data visualization", "excel", "tableau", "power bi", "qlikview",
    "matlab", "r programming", "sas", "stata", "scala", "haskell", "rust", "cobol", "fortran",
    "assembly", "unity", "unreal engine", "blockchain", "cryptography", "cybersecurity", "penetration testing",
    "networking", "tcp/ip", "dns", "dhcp", "firewalls", "vpn", "siem", "incident response",
    "compliance", "gdpr", "iso27001", "itil", "project management", "business analysis", "ux/ui design",
    "waterfall methodology", "couchdb", "firebase", "aws lambda", "azure functions", "gcp cloud functions",
    "serverless", "edge computing", "iot", "raspberry pi", "arduino", "robotics", "automation",
    "virtualization", "vmware", "hyper-v", "citrix", "cloud computing", "saas", "paas", "iaas",
    "crm", "erp", "sap", "oracle", "salesforce", "slack", "trello",
    "fme", "data transformation", "arcgis", "qgis", "geospatial", "gps", "remote sensing", "cartography",
    "autocad", "revit", "solidworks", "3d modeling", "bim", "building information modeling",
    "project scheduling", "cloud storage", "dropbox", "google drive", "one drive", "oop", "functional programming",
    "restful services", "web development", "mobile development", "responsive design", "cross-platform development",
    "performance optimization", "scalability", "load balancing", "high availability", "disaster recovery",
    "monitoring", "logging", "alerting", "prometheus", "grafana", "elk stack", "kibana", "logstash", "kotlin",
    "flutter", "react native", "xamarin", "mobile apps", "app development", "game development",
    "augumented reality", "virtual reality", "vr", "ar", "3d graphics", "opengl", "directx", "scrum master",
    "software architecture", "design patterns", "uml", "system design", "code review", "unit testing", "integration testing",
    "test driven development", "bdd", "junit", "pytest", "mocha", "chai", "cypress", "github", "gitlab", "bitbucket", "version control",
    "sorting algorithms", "data structures", "linked lists", "trees", "graphs", "hash tables", "queues", "stacks", "algorithms", "complexity analysis",
    "continuous integration", "continuous deployment", "infrastructure as code", "iac", "configuration management", "openai", "gpt-3", "chatgpt", "dall-e",
    "machine translation", "speech recognition", "computer graphics", "image processing", "signal processing", "quantum computing"
]

QUALIFICATION_KEYWORDS = [
    "degree", "bachelor", "masters", "diploma", "certificate",
    "certification", "msc", "bsc", "microsoft certified", "aws certified",
    "cisa"
]

SOFT_SKILLS = [
    "communication", "teamwork", "presentation", "leadership",
    "time management", "problem solving", "critical thinking",
    "adaptability", "creativity", "work ethic", "interpersonal skills",
    "conflict resolution", "empathy", "collaboration", "decision making",
    "organization", "attention to detail", "multitasking", "stress management",
    "negotiation", "networking", "public speaking", "active listening",
    "flexibility", "patience", "positivity", "self-motivation",
    "dependability", "initiative", "responsibility"
]

EXPERIENCE_PATTERNS = [
    r"\b[0-9]+ ?\+? years? experience\b",
    r"\bexperience with\b",
    r"\bused\b"
    r"\bworked on\b",
    r"\bworked with\b"
    r"\bfamiliar with\b",
    r"\bproficient in\b",
    r"\bexpert in\b"
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
