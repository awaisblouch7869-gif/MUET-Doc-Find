"""Step 2a: cut selected prospectus sections out of the PDF into data/muet_passages.json.

Needs the optional package pypdf.  Run from the project folder:  python scripts/build_muet_passages.py
"""
import json
from pathlib import Path
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent

pdf_path = ROOT / "data/source_documents/MUET_UG_Prospectus_2025_26.pdf"
output_path = ROOT / "data/muet_passages.json"
reader = PdfReader(str(pdf_path))
selections = [
    {
        "passage_id": "MUET-P001",
        "pdf_page": 6,
        "printed_page": "vi",
        "category": "academic_calendar",
        "start": "ACADEMIC CALENDAR FOR BACHELOR’S DEGREE PROGRAMS",
        "end": "SEMESTER: FALL 2025",
    },
    {
        "passage_id": "MUET-P002",
        "pdf_page": 8,
        "printed_page": "1",
        "category": "university_information",
        "start": "1.1 The University",
        "end": "In 2009,",
    },
    {
        "passage_id": "MUET-P003",
        "pdf_page": 38,
        "printed_page": "31",
        "category": "computer_systems_engineering",
        "start": "3.3 Department of Computer Systems Engineering",
        "end": "Vision of the Department",
    },
    {
        "passage_id": "MUET-P004",
        "pdf_page": 100,
        "printed_page": "93",
        "category": "computer_science",
        "start": "5.2 Bachelor of Science in Computer Science (BSCS)",
        "end": "Vision of the Department",
    },
]
records = []
for item in selections:
    text = reader.pages[item["pdf_page"] - 1].extract_text() or ""
    start_index = text.find(item["start"])
    end_index = text.find(item["end"], start_index + len(item["start"]))
    if start_index == -1 or end_index == -1:
        raise ValueError(
            f"Could not locate passage boundaries for {item['passage_id']} "
            f"on PDF page {item['pdf_page']}"
        )
    passage_text = text[start_index:end_index].strip()
    records.append({
        "passage_id": item["passage_id"],
        "document_id": "MUET-UG-PROSPECTUS-2025-26",
        "title": "MUET Undergraduate Prospectus 2025-26",
        "source_url": (
            "https://admissions.muet.edu.pk/wp-content/uploads/2026/04/"
            "UG_Prospectus_2025_26.pdf"
        ),
        "version": "2025-26",
        "pdf_page": item["pdf_page"],
        "printed_page": item["printed_page"],
        "category": item["category"],
        "text": passage_text,
        "synthetic": False,
    })
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(
    json.dumps(records, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
print("Official passages saved:", len(records))
print("Output:", output_path.resolve())
for record in records:
    print(
        record["passage_id"],
        "| PDF page:", record["pdf_page"],
        "| Characters:", len(record["text"]),
    )
