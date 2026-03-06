import re

BAD_PREFIXES = (
    "ability to ",
    "knowledge of ",
    "understanding of ",
    "experience with ",
    "experience in ",
    "strong ",
    "good ",
)

BAD_EXACT = {
    "&", "and", "a", "an", "the", "etc", "****",
}

def clean_skill(raw: str) -> str | None:
    if not raw:
        return None

    s = raw.strip().lower()

    # drop obvious trash
    if s in BAD_EXACT:
        return None

    # drop junk prefixes
    for p in BAD_PREFIXES:
        if s.startswith(p):
            s = s[len(p):].strip()

    # remove hanging "(e.g" / incomplete brackets
    s = re.sub(r"\(e\.g.*$", "", s).strip()
    s = s.strip(" .,:;|/\\-–—()[]{}\"'")

    # very short / meaningless tokens
    if len(s) < 2:
        return None

    # reduce ultra-long sentences (usually not a skill)
    # keep if it contains obvious IT keywords
    it_hint = any(k in s for k in ["sql", "python", "aws", "azure", "linux", "java", "docker", "kubernetes", "cisco", "network", "security"])
    if len(s.split()) > 6 and not it_hint:
        return None

    return s
