//formatters.js - used to make a cleaner frontend layout
//function to trim and clean displayed values
export function cleanDisplayValue(value) {
  if (!value) {
    return "";
  }
  let cleaned = String(value).trim();
  if (cleaned.startsWith("{") && cleaned.endsWith("}")) {
    cleaned = cleaned.slice(1, -1).trim();
  }
  cleaned = cleaned.replace(/"/g, "").trim();

  return cleaned;
}
//function to add TitleCase to certain words to make it look cleaner for the user
export function toTitleCaseSkill(value) {
  if (!value) {
    return "";
  }

  const cleanedInput = cleanDisplayValue(value).toLowerCase();

  const specialCases = {
    "c#": "C#",
    "ci/cd": "CI/CD",
    "cdn": "CDN (Content Delivery Network)",
    "grpc": "gRPC",
    "rest api": "REST API",
    "api": "API",
    "apis": "APIs",
    "mysql": "mySQL",
    "sql": "SQL",
    "nosql": "NoSQL",
    "aws": "AWS",
    "html": "HTML",
    "css": "CSS",
    "go": "Golang",
    "http": "HTTP",
    "https": "HTTPS",
    "dns": "DNS",
    "tcp/ip": "TCP/IP",
    "gcp": "GCP",
    "ios": "iOS",
    "it project management": "IT Project Management",
    "json": "JSON",
    "openapi": "Open API",
    "postgresql": "PostgreSQL",
    "php": "PHP",
    "mongodb": "MongoDB",
    "nlp": "NLP",
    "oop": "OOP", 
    "ui": "UI",
    "ux": "UX",
    "spacy": "spaCy",
    "sdk": "SDK",
    "xml": "XML",
    "yaml": "YAML",
    "beginner": "Beginner",
    "intermediate": "Intermediate",
    "advanced": "Advanced",
    "introductory": "Introductory",
    "mixed": "Mixed",
  };

  if (specialCases[cleanedInput]) {
    return specialCases[cleanedInput];
  }

  return cleanedInput
    .split(" ")
    .map((word) => {
      if (!word) {
        return "";
      }

      return word.charAt(0).toUpperCase() + word.slice(1);
    })
    .join(" ");
}
//function to add "hrs" after a duration number
export function formatDurationHours(value) {
  const cleaned = cleanDisplayValue(value);

  if (!cleaned) {
    return "";
  }

  const numeric = Number(cleaned);

  if (!Number.isNaN(numeric)) {
    return `${numeric} hrs`;
  }

  return `${cleaned} hrs`;
}