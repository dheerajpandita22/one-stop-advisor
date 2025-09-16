import pytesseract
from PIL import Image
import io
import re

def parse_marksheet(file_storage):
    """
    Extracts marks from an uploaded marksheet image using OCR.
    Returns a list of dicts with subject_name, obtained, max, etc.
    """
    try:
        img = Image.open(io.BytesIO(file_storage.read()))
        text = pytesseract.image_to_string(img)
    except Exception:
        return []

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    subjects = []
    for l in lines:
        # Pattern: SubjectName 95/100
        m = re.search(r"([A-Za-z ]+)\s+(\d{1,3})\s*[/\-]\s*(\d{2,3})", l)
        if m:
            subjects.append({
                "exam_type": "10",
                "subject_code": "",
                "subject_name": m.group(1).strip(),
                "obtained": int(m.group(2)),
                "max": int(m.group(3)),
                "confidence": 0.7
            })
    return subjects