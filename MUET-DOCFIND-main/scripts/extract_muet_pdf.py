"""Step 1: extract the text of the MUET prospectus PDF into data/extracted_documents/.

Needs the optional package pypdf.  Run from the project folder:  python scripts/extract_muet_pdf.py
"""
from pathlib import Path
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent

source = ROOT / "data/source_documents/MUET_UG_Prospectus_2025_26.pdf"
output = ROOT / "data/extracted_documents/MUET_UG_Prospectus_2025_26.txt"
reader = PdfReader(str(source))
output.parent.mkdir(parents=True, exist_ok=True)
pages_with_text = 0
with output.open("w", encoding="utf-8") as file:
    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            pages_with_text += 1
        file.write(f"\n\n===== PDF PAGE {page_number} =====\n\n")
        file.write(text)
print("Total PDF pages:", len(reader.pages))
print("Pages containing text:", pages_with_text)
print("Extracted text file:", output.resolve())
print("Output file size:", output.stat().st_size, "bytes")
