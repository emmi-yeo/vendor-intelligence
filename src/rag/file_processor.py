import io
import pdfplumber
from typing import List


def extract_text_from_pdf(file_bytes: bytes) -> str:
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text


def simple_chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap

    return chunks


def process_uploaded_file(file) -> List[str]:
    """
    Accepts Streamlit uploaded file.
    Returns list of text chunks.
    """
    if file.type == "application/pdf":
        text = extract_text_from_pdf(file.read())
    else:
        text = file.read().decode("utf-8")

    chunks = simple_chunk_text(text)
    return chunks