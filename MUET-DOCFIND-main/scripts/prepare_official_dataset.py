"""Step 3: convert data/muet_official_passages.json into the format main.py reads
(data/muet_official_passages_compatible.json).

Note: muet_official_passages.json is the 4 prospectus passages followed by the 4 calendar
passages (checked identical); no script currently merges them, so that step was done by hand.

Run from the project folder:  python scripts/prepare_official_dataset.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

source_path = ROOT / "data/muet_official_passages.json"
output_path = ROOT / "data/muet_official_passages_compatible.json"
records = json.loads(source_path.read_text(encoding="utf-8"))
converted = []
for item in records:
    converted.append({
        "passage_id": item["passage_id"],
        "document_id": item["document_id"],
        "title": item["title"],
        "category": item["category"],
        "source": item["source_url"],
        "version": item["version"],
        "date": "Not specified in source",
        "text": item["text"],
        "synthetic": False,
        "pdf_page": item["pdf_page"],
    })
output_path.write_text(
    json.dumps(converted, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
print("Compatible official passages:", len(converted))
print("Saved:", output_path.resolve())
print("Required fields check:")
required = [
    "passage_id", "document_id", "title", "category",
    "source", "version", "date", "text",
]
for item in converted:
    missing = [field for field in required if not item.get(field)]
    print(item["passage_id"], "|", "PASS" if not missing else f"MISSING: {missing}")

