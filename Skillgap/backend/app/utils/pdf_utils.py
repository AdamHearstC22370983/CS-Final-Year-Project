# pdf_utils.py

# A Utility functions file used to extract and clean text from PDF files only, using pdfplumber.
# As well as:
# Iterating over all pages
# Join page text with clear separators
# Normalise whitespace

from io import BytesIO
import pdfplumber

def extract_pdf_text(file_bytes: bytes) -> str:
# Extracts text from a PDF file given as raw bytes.
# :param file_bytes will read the file content from UploadFile.read()
# :return will output the extracted raw text as a string

    text_chunks = []

    # pdfplumber works with file-like objects, so wrap bytes in BytesIO
    with pdfplumber.open(BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_chunks.append(page_text)

    full_text = "\n\n".join(text_chunks)
    return full_text
