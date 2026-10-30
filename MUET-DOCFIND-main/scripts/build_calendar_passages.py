"""Step 2b: cut the academic-calendar text into data/muet_calendar_passages.json.

Run from the project folder:  python scripts/build_calendar_passages.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

source_path = ROOT / "data/extracted_documents/MUET_Academic_Calendar_2025_26.txt"
output_path = ROOT / "data/muet_calendar_passages.json"
text = source_path.read_text(encoding="utf-8")
sections = [
    {
        "passage_id": "MUET-CAL-P001",
        "category": "semester_duration_attendance",
        "start": "Duration of a Semester:",
        "end": "SEMESTER: FALL 2025",
    },
    {
        "passage_id": "MUET-CAL-P002",
        "category": "fall_2025_schedule",
        "start": "SEMESTER: FALL 2025",
        "end": "SEMESTER: SPRING 2026",
    },
    {
        "passage_id": "MUET-CAL-P003",
        "category": "spring_2026_schedule",
        "start": "SEMESTER: SPRING 2026",
        "end": "WINTER VACATION:",
    },
    {
        "passage_id": "MUET-CAL-P004",
        "category": "vacations_summer_dates",
        "start": "WINTER VACATION:",
        "end": None,
    },
]
records = []
for section in sections:
    start_index = text.find(section["start"])
    if start_index == -1:
        raise ValueError(f"Section not found: {section['passage_id']}")
    if section["end"]:
        end_index = text.find(section["end"], start_index + len(section["start"]))
        if end_index == -1:
            raise ValueError(f"End marker not found: {section['passage_id']}")
        passage_text = text[start_index:end_index].strip()
    else:
        passage_text = text[start_index:].strip()
    records.append({
        "passage_id": section["passage_id"],
        "document_id": "MUET-ACADEMIC-CALENDAR-2025-26",
        "title": "MUET Academic Calendar 2025-26",
        "source_url": "https://www.muet.edu.pk/academics/academic-calendar",
        "version": "2025-26",
        "pdf_page": 1,
        "category": section["category"],
        "text": passage_text,
        "synthetic": False,
        "verification_note": (
            "Source text preserved as published; check inconsistent Fall 2026 date."
            if section["passage_id"] == "MUET-CAL-P004"
            else ""
        ),
    })
output_path.write_text(
    json.dumps(records, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
print("Calendar passages saved:", len(records))
print("Output:", output_path.resolve())
for record in records:
    print(record["passage_id"], "|", record["category"], "|", len(record["text"]), "characters")
