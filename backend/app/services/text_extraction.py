#text_extraction.py

#High-level text extraction service. It delas with:
# Detecting file type (PDF/DOCX) from filename/content type
# Using pdf_utils / docx_utils utility programs to extract text
# Applies advanced cleaning which includes:
#   normalise line breaks
#   remove duplicate blank lines
#   trim whitespace
#   de-duplicate consecutive lines


import re
from fastapi import HTTPException, UploadFile

from app.utils.pdf_utils import extract_pdf_text
from app.utils.docx_utils import extract_docx_text


def _normalise_whitespace(text: str) -> str:
# Normalises whitespace and line breaks in extracted text.
# Converts Windows/Mac newlines to '\n'
# Strips leading/trailing spaces on each line
# Removes multiple blank lines
    # If the text is empty, return as is
    if not text:
        return ""

    # Normalise line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Split into lines and strip each
    lines = [line.strip() for line in text.split("\n")]

    # Remove consecutive empty lines
    cleaned_lines = []
    previous_blank = False
    # Iterate through lines and add to cleaned_lines if not duplicate blank
    for line in lines:
        if line == "":
            if not previous_blank:
                cleaned_lines.append(line)
            previous_blank = True
        else:
            cleaned_lines.append(line)
            previous_blank = False

    return "\n".join(cleaned_lines).strip()


def _deduplicate_consecutive_lines(text: str) -> str:
# Removes consecutive duplicate lines, which often appear due to header/footer repetition in PDFs.
    # If the text is empty, return as is
    if not text:
        return ""

    lines = text.split("\n")
    result = []
    last_line = None

    # Iterate through lines and add to result if text is different from last line
    for line in lines:
        if line != last_line:
            result.append(line)
        last_line = line
    # Join the result back into a single string
    return "\n".join(result)


def clean_extracted_text(raw_text: str) -> str:
# Applies advanced cleaning to raw extracted text.
    
    # cleans data by normalising whitespace and removing duplicate lines
    text = _normalise_whitespace(raw_text)
    text = _deduplicate_consecutive_lines(text)

    # collapse excessive spaces inside lines
    text = re.sub(r"[ \t]+", " ", text)

    return text

def extract_text_from_upload(file: UploadFile, file_bytes: bytes) -> str:
# High-level function used by FastAPI endpoint.
# Determines file type from filename/content type
# Routes to the correct extractor while cleaning the file

    filename = file.filename.lower() if file.filename else ""
    content_type = (file.content_type or "").lower()

    # Decide based on extension first
    if filename.endswith(".pdf") or "pdf" in content_type:
        raw_text = extract_pdf_text(file_bytes)
    elif filename.endswith(".docx") or "officedocument" in content_type:
        raw_text = extract_docx_text(file_bytes)
    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload a PDF or DOCX file."
        )

    cleaned_text = clean_extracted_text(raw_text)
    return cleaned_text