import pdfplumber
import docx
from pathlib import Path

def load_document(path):
    """Load text from various file formats."""
    path = Path(path)
    if path.suffix == '.txt':
        with open(path) as f:
            return f.read()
    elif path.suffix == '.pdf':
        with pdfplumber.open(path) as pdf:
            return '\n'.join(page.extract_text() for page in pdf.pages)
    elif path.suffix == '.md':
        with open(path) as f:
            return f.read()
    elif path.suffix == '.docx':
        doc = docx.Document(path)
        return '\n'.join(para.text for para in doc.paragraphs)
    else:
        raise ValueError(f"Unsupported file type: {path.suffix}")