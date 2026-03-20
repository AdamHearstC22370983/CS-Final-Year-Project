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
    "ci/cd": "CI/CD",
    "grpc": "gRPC",
    "rest api": "REST API",
    "api": "API",
    "apis": "APIs",
    "sql": "SQL",
    "aws": "AWS",
    "html": "HTML",
    "css": "CSS",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "react.js": "React.js",
    "node.js": "Node.js",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "microservices": "Microservices",
    "go": "Go",
    "rust": "Rust",
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