# docx_utils.py

# A Utility functions file used to extract text from DOCX files (Word documents).
# Reads all paragraphs and Joins with newlines

from io import BytesIO
from docx import Document

def extract_docx_text(file_bytes: bytes) -> str:
# Extracts text from a DOCX file given as raw bytes.
# :param file_bytes will read the file content from UploadFile.read()
# :return will output the extracted raw text as a string
    docx_file = BytesIO(file_bytes)
    document = Document(docx_file)

    paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
    full_text = "\n".join(paragraphs)
    return full_text