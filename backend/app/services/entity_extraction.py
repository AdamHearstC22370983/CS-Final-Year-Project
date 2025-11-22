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

# Below are keyword lists and patterns for rule-based extraction.
# In a production system, these would be more comprehensive or replaced with ML models.
# I used Copilot to help add more keywords to the list but I wish to use an API key here to extract from ESCO directly.
TECH_KEYWORDS = [
    # Core programming
    "python", "java", "javascript", "typescript", "c# programming", "c++ programming", "c programming", 
    "go", "rust", "scala", "kotlin", "swift", "dart", "php", "ruby",
    "sql", "nosql", "bash", "powershell", "shell scripting",
    # Web + mobile
    "html", "css", "react", "nextjs", "angular", "vue", "svelte",
    "node", "express", "django", "flask", "fastapi", "spring", "laravel",
    "react native", "flutter", "xamarin", "kivy", "mobile development",
    # Databases & data engineering
    "postgresql", "mysql", "sqlite", "oracle", "mongodb", "couchdb",
    "redis", "elasticsearch", "cassandra",
    "data engineering", "data pipeline", "etl", "elt",
    "airflow", "dbt", "snowflake", "bigquery", "redshift",
    # Machine Learning + AI
    "machine learning", "deep learning", "artificial intelligence",
    "data science", "nlp", "computer vision", "transformers",
    "llm", "openai", "chatgpt", "gpt", "tensorflow", "keras", "pytorch",
    "scikit-learn", "huggingface", "bert", "yolo", "lstm",
    "autoencoders", "gan", "xgboost", "lightgbm",
    # Data analytics & visualisation
    "data analysis", "data mining", "data cleaning",
    "tableau", "power bi", "qlik", "microsoft excel", "microsoft databases",
    "pandas", "numpy", "matplotlib", "seaborn", "statistics", "sql analytics",
    "spark streaming", "kinesis", "flink", "looker", "mode analytics",
    # Cloud computing
    "aws", "azure", "gcp", "cloud computing", "serverless",
    "aws lambda", "azure functions", "cloud functions",
    "saas", "paas", "iaas",
    #Cybersecurity/ Cloud & DevOps
    "burp suite", "wireshark", "nmap", "owasp", "metasploit",
    "cloudtrail", "cloudwatch", "aws ec2", "aws s3", "aws rds",
    "kms", "iam", "azure ad", "azure devops",
    # DevOps, CI/CD, and automation
    "docker", "kubernetes", "containerisation", "devops",
    "ci/cd", "jenkins", "github", "github actions", "gitlab ci",
    "ansible", "terraform", "helm", "prometheus", "grafana",
    "infrastructure as code", "iac",
    # Networking + security
    "cybersecurity", "penetration testing", "ceh", "network security",
    "tcp/ip", "vpn", "firewalls", "siem", "splunk",
    "incident response", "forensics", "encryption", "cryptography",
    "iso 27001", "nist",
    # Software engineering & architecture
    "microservices", "rest", "graphql", "api", "system design",
    "uml", "design patterns", "object oriented programming", "functional programming",
    "unit testing", "tdd", "bdd", "integration testing",
    # Cloud-native + distributed systems
    "event-driven architecture", "kafka", "rabbitmq", "pubsub",
    "grpc", "consul", "service mesh", "envoy", "istio",
    # GIS / Geospatial
    "fme", "arcgis", "qgis", "geospatial", "remote sensing",
    "cartography", "gps", "coordinate systems", "postgis",
    "lidar", "geoprocessing", "spatial analysis", "geocoding", 
    # Robotics, hardware, IoT
    "robotics", "arduino", "raspberry pi", "embedded systems",
    "iot", "edge computing",
    # Virtualisation
    "virtualization", "vmware", "hyper-v", "docker swarm",
    # XR / 3D / Game Dev
    "unity", "unreal", "3d modeling", "opengl", "directx",
    "augmented reality", "virtual reality", "vr", "ar",
    #Software Quality & Testing
    "selenium", "playwright", "postman", "cucumber",
    # Scientific & HPC
    "matlab", "r", "stata", "fortran", "cobol",
    "quantum computing", "parallel computing"
]

QUALIFICATION_KEYWORDS = [
    "degree", "bachelor", "diploma", "professional certificate",
    "certification", "bsc", "higher diploma",
    # General certs
    "ielts", "edX certificate", "coursera certificate", "udemy certificate",
    "pluralsight certificate", "linkedin learning certificate", "bootcamp",
    # Cloud certs
    "aws certified", "azure certified", "gcp certified",
    "aws cloud practitioner", "aws solutions architect",
    "azure fundamentals", "azure administrator",
    "gcp associate engineer",
    # Cybersecurity certs
    "cisa", "ceh", "comptia", "security+", "network+",
    "cybersecurity certificate",
    # Data + analytics certs
    "google data analytics", "microsoft certified",
    "power bi certification", "tableau certification",
    # Vendor certs
    "oracle certified", "red hat certified", "cisco certified",
]

SOFT_SKILLS = [
    # Core communication
    "communication skills", "public speaking skills", "presentation", "presentation skills",
    "active listening skills", "negotiation skills", "interpersonal skills",
    # Collaboration
    "teamwork skills", "team player", "collaboration", "leadership skills",
    "facilitation", "mentoring experience", "coaching experience",
    # Work behaviour
    "time management skills", "organization skills", "attention to detail",
    "multitasking", "responsibility", "initiative", "work ethic",
    "dependability", "self-motivation",
    # Thinking skills
    "problem solving skills", "critical thinking skills", "analytical thinking skills",
    "decision making", "creativity",
    # Adaptability skills
    "adaptability", "flexibility", "stress management",
    # Interview-related competencies
    "interview skills", "interviewing", "self-presentation",
    "confidence", "professionalism",
    # Business communication
    "stakeholder management", "written communication",
    "report writing", "stakeholder communication", "client interaction",
    "meeting facilitation"
]

EXPERIENCE_PATTERNS = [
    r"\b[0-9]+ ?\+? years? experience\b",
    r"\bexperience with\b",
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
